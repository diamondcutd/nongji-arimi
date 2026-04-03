"""
농지은행(fbo.or.kr) 매물 크롤러
Playwright를 사용하여 csrfToken 세션 처리 및 매물 목록 수집
"""
import asyncio
import logging
import re
from datetime import datetime
from playwright.async_api import async_playwright, Page
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import async_session
from app.models import Listing
from app.utils.region_codes import SIDO_CODES, SIGUN_CODES

logger = logging.getLogger(__name__)

BASE_URL = "https://www.fbo.or.kr"
LIST_URL = f"{BASE_URL}/fsle/trde/TrdeList.do?menuId=020020"

# 크롤링 간 딜레이 (초) - 서버 차단 방지
REQUEST_DELAY = 2.5


def parse_price(text: str) -> int | None:
    """'1,234,567' 형태의 금액 문자열을 int로 변환"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d]", "", text.strip())
    return int(cleaned) if cleaned else None


def parse_area(text: str) -> int | None:
    """'1,234' 형태의 면적 문자열을 int로 변환"""
    if not text:
        return None
    cleaned = re.sub(r"[^\d.]", "", text.strip())
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def parse_date(text: str):
    """'2025.03.24' 또는 '2025-03-24' 형태의 날짜 문자열 파싱"""
    if not text or not text.strip():
        return None
    cleaned = text.strip().replace(".", "-")
    try:
        return datetime.strptime(cleaned, "%Y-%m-%d").date()
    except ValueError:
        return None


def extract_listing_key(onclick_or_href: str) -> str | None:
    """onclick 또는 href에서 reqFlndid 값 추출"""
    match = re.search(r"reqFlndid[=,'\"](\w+)", onclick_or_href)
    if match:
        return match.group(1)
    # 다른 패턴: 함수 인자에서 추출
    match = re.search(r"fn_detail\(['\"]?(\w+)['\"]?\)", onclick_or_href)
    if match:
        return match.group(1)
    return None


def extract_trade_biz_type(type_text: str) -> tuple[str | None, str | None]:
    """
    '매도-맞춤형', '임대-공공임대' 등에서 trade_type과 biz_type 분리
    """
    if not type_text:
        return None, None
    parts = type_text.strip().split("-", 1)
    trade_type = parts[0].strip() if parts else None
    biz_type = parts[1].strip() if len(parts) > 1 else None
    return trade_type, biz_type


def extract_region_codes(address: str) -> tuple[str | None, str | None, str | None]:
    """
    주소 문자열에서 시도코드, 시군구코드, 읍면동 추출
    예: '경상남도 함안군 칠원읍' → ('38', '38100', '칠원읍')
    """
    if not address:
        return None, None, None

    sido_cd = None
    sigun_cd = None
    eupmyeondong = None

    # 시도 매칭
    for code, name in SIDO_CODES.items():
        # 약칭 매칭 (경상남도 → 경남, 서울특별시 → 서울 등)
        short_name = name[:2]
        if name in address or short_name in address:
            sido_cd = code
            break

    if sido_cd:
        # 시군구 매칭
        siguns = SIGUN_CODES.get(sido_cd, {})
        for code, name in siguns.items():
            if name in address:
                sigun_cd = code
                break

    # 읍면동 추출
    emd_match = re.search(r"(\S+[읍면동리])\s", address + " ")
    if emd_match:
        eupmyeondong = emd_match.group(1)

    return sido_cd, sigun_cd, eupmyeondong


async def crawl_listings(
    sido_cd: str | None = None,
    sigun_cd: str | None = None,
) -> list[dict]:
    """
    농지은행 매물 목록 크롤링

    1. Playwright로 브라우저 실행
    2. fbo.or.kr 접속 → csrfToken 세션 자동 획득
    3. 매물 목록 페이지 순회하며 파싱
    4. 신규 매물 DB 저장 (중복 방지)
    5. 신규 매물 리스트 반환
    """
    new_listings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        try:
            # 1) 메인 페이지 접속하여 세션/쿠키 획득
            logger.info("농지은행 접속 중...")
            await page.goto(BASE_URL, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(REQUEST_DELAY)

            # 2) 매물 목록 페이지로 이동
            logger.info("매물 목록 페이지 접속...")
            await page.goto(LIST_URL, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(REQUEST_DELAY)

            # 3) 검색 조건 설정 (시도/시군구 선택)
            if sido_cd:
                await _select_region(page, sido_cd, sigun_cd)
                await asyncio.sleep(REQUEST_DELAY)

            # 4) 진행중 매물만 필터 (schStat=Y 검색 실행)
            await _click_search(page)
            await asyncio.sleep(REQUEST_DELAY)

            # 5) 페이지네이션 순회하며 매물 수집
            page_no = 1
            while True:
                logger.info(f"페이지 {page_no} 파싱 중...")
                rows = await _parse_listing_table(page)

                if not rows:
                    logger.info(f"페이지 {page_no}: 매물 없음, 크롤링 종료")
                    break

                # DB 저장
                saved = await _save_listings(rows)
                new_listings.extend(saved)

                # 다음 페이지 존재 확인 및 이동
                has_next = await _goto_next_page(page, page_no + 1)
                if not has_next:
                    logger.info("마지막 페이지 도달, 크롤링 종료")
                    break

                page_no += 1
                await asyncio.sleep(REQUEST_DELAY)

        except Exception as e:
            logger.error(f"크롤링 오류: {e}", exc_info=True)
        finally:
            await browser.close()

    logger.info(f"크롤링 완료. 신규 매물 {len(new_listings)}건")
    return new_listings


async def _select_region(page: Page, sido_cd: str, sigun_cd: str | None):
    """시도/시군구 드롭다운 선택"""
    try:
        # 시도 선택
        sido_select = page.locator("select[name='schSidoCd'], #schSidoCd")
        if await sido_select.count() > 0:
            await sido_select.select_option(value=sido_cd)
            await asyncio.sleep(1)

            # 시군구 선택 (시도 선택 후 동적 로딩)
            if sigun_cd:
                sigun_select = page.locator("select[name='schSigunCd'], #schSigunCd")
                if await sigun_select.count() > 0:
                    await asyncio.sleep(1)  # 시군구 목록 로딩 대기
                    await sigun_select.select_option(value=sigun_cd)
    except Exception as e:
        logger.warning(f"지역 선택 실패: {e}")


async def _click_search(page: Page):
    """검색 버튼 클릭"""
    try:
        # 검색 버튼 찾기 (여러 가능한 셀렉터)
        search_btn = page.locator(
            "button:has-text('검색'), "
            "a:has-text('검색'), "
            "input[type='submit'][value='검색'], "
            ".btn_search"
        )
        if await search_btn.count() > 0:
            await search_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception as e:
        logger.warning(f"검색 버튼 클릭 실패: {e}")


async def _parse_listing_table(page: Page) -> list[dict]:
    """
    매물 목록 테이블 파싱
    컬럼: 구분 / 농지 소재지 / 지목 / 필지수 / 총면적(㎡) / 희망가(원) / 신청기한 / 신청자 수
    """
    rows_data = []

    try:
        # 테이블 행 선택 (tbody > tr)
        rows = page.locator("table.tbl_list tbody tr, table.board_list tbody tr, .list_table tbody tr")
        count = await rows.count()

        if count == 0:
            # 대체 셀렉터
            rows = page.locator("table tbody tr")
            count = await rows.count()

        for i in range(count):
            row = rows.nth(i)
            cells = row.locator("td")
            cell_count = await cells.count()

            if cell_count < 6:
                continue

            try:
                # 각 셀 텍스트 추출
                type_text = (await cells.nth(0).text_content() or "").strip()
                address = (await cells.nth(1).text_content() or "").strip()
                land_category = (await cells.nth(2).text_content() or "").strip()
                parcel_count_text = (await cells.nth(3).text_content() or "").strip()
                area_text = (await cells.nth(4).text_content() or "").strip()
                price_text = (await cells.nth(5).text_content() or "").strip()

                deadline_text = ""
                applicant_text = ""
                if cell_count > 6:
                    deadline_text = (await cells.nth(6).text_content() or "").strip()
                if cell_count > 7:
                    applicant_text = (await cells.nth(7).text_content() or "").strip()

                # 상세 링크에서 listing_key 추출
                listing_key = None
                link = row.locator("a[onclick], a[href*='reqFlndid']")
                if await link.count() > 0:
                    onclick = await link.first.get_attribute("onclick") or ""
                    href = await link.first.get_attribute("href") or ""
                    listing_key = extract_listing_key(onclick) or extract_listing_key(href)

                # listing_key가 없으면 주소+면적+금액으로 생성
                if not listing_key:
                    listing_key = f"{address}_{area_text}_{price_text}".replace(" ", "")

                trade_type, biz_type = extract_trade_biz_type(type_text)
                sido_cd, sigun_cd, eupmyeondong = extract_region_codes(address)

                detail_url = None
                if listing_key and "reqFlndid" not in (listing_key or ""):
                    detail_url = f"{BASE_URL}/fsle/trde/TrdeDtl.do?reqFlndid={listing_key}"

                rows_data.append({
                    "listing_key": listing_key,
                    "trade_type": trade_type,
                    "biz_type": biz_type,
                    "address": address,
                    "sido_cd": sido_cd,
                    "sigun_cd": sigun_cd,
                    "eupmyeondong": eupmyeondong,
                    "land_category": land_category if land_category in ("전", "답", "과수원") else None,
                    "parcel_count": parse_area(parcel_count_text),
                    "total_area": parse_area(area_text),
                    "price": parse_price(price_text),
                    "deadline": parse_date(deadline_text),
                    "applicant_count": parse_area(applicant_text),
                    "detail_url": detail_url,
                })

            except Exception as e:
                logger.warning(f"행 파싱 실패 (행 {i}): {e}")
                continue

    except Exception as e:
        logger.error(f"테이블 파싱 실패: {e}")

    return rows_data


async def _save_listings(rows: list[dict]) -> list[dict]:
    """
    매물 DB 저장 (중복 방지: listing_key UNIQUE)
    PostgreSQL의 INSERT ... ON CONFLICT DO NOTHING 사용
    """
    new_listings = []

    async with async_session() as session:
        for row in rows:
            # 중복 확인
            result = await session.execute(
                select(Listing).where(Listing.listing_key == row["listing_key"])
            )
            existing = result.scalar_one_or_none()

            if existing is None:
                listing = Listing(
                    listing_key=row["listing_key"],
                    trade_type=row["trade_type"],
                    biz_type=row["biz_type"],
                    address=row["address"],
                    sido_cd=row["sido_cd"],
                    sigun_cd=row["sigun_cd"],
                    eupmyeondong=row["eupmyeondong"],
                    land_category=row["land_category"],
                    parcel_count=row["parcel_count"],
                    total_area=row["total_area"],
                    price=row["price"],
                    deadline=row["deadline"],
                    applicant_count=row["applicant_count"],
                    detail_url=row["detail_url"],
                    is_new=True,
                )
                session.add(listing)
                new_listings.append(row)
                logger.info(f"신규 매물: {row['address']} ({row['land_category']}) {row['total_area']}㎡")

        await session.commit()

    return new_listings


async def _goto_next_page(page: Page, next_page_no: int) -> bool:
    """다음 페이지로 이동. 성공하면 True, 마지막 페이지면 False"""
    try:
        # 페이지네이션 링크 찾기
        # 방법 1: 페이지 번호 링크 클릭
        next_link = page.locator(
            f"a:has-text('{next_page_no}'), "
            f"a[onclick*='currentPageNo={next_page_no}'], "
            f"a[href*='currentPageNo={next_page_no}']"
        )

        if await next_link.count() > 0:
            await next_link.first.click()
            await page.wait_for_load_state("networkidle", timeout=10000)
            return True

        # 방법 2: '다음' 버튼
        next_btn = page.locator("a:has-text('다음'), a.btn_next, .paging_next")
        if await next_btn.count() > 0:
            is_disabled = await next_btn.first.get_attribute("class") or ""
            if "disabled" not in is_disabled:
                await next_btn.first.click()
                await page.wait_for_load_state("networkidle", timeout=10000)
                return True

    except Exception as e:
        logger.warning(f"페이지 이동 실패: {e}")

    return False


async def crawl_all_regions():
    """전체 시도를 순회하며 크롤링 (매일 실행용)"""
    all_new = []
    for sido_cd in SIDO_CODES:
        logger.info(f"시도 크롤링: {SIDO_CODES[sido_cd]} ({sido_cd})")
        new = await crawl_listings(sido_cd=sido_cd)
        all_new.extend(new)
        await asyncio.sleep(REQUEST_DELAY)
    return all_new


# 단독 실행 테스트
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    async def main():
        logger.info("=== 농지은행 크롤러 테스트 시작 ===")
        # 전체 매물 크롤링 (지역 필터 없이)
        results = await crawl_listings()
        logger.info(f"=== 크롤링 완료: 신규 매물 {len(results)}건 ===")
        for r in results[:5]:
            logger.info(f"  - {r['address']} | {r['land_category']} | {r['total_area']}㎡ | {r['price']}원")

    asyncio.run(main())
