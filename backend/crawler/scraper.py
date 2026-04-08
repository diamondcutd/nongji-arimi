"""농지은행 매물 목록 크롤러 — Playwright 기반, 시도별 전국 수집"""

import logging
import re
import time
from datetime import date, datetime
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

FBO_BASE_URL = "https://www.fbo.or.kr/fsle/trde/TrdeList.do"

# 전국 시도 코드 (2024~ 강원특별자치도=51, 전북특별자치도=52)
SIDO_CODES = [
    "11", "26", "27", "28", "29", "30", "31", "36",
    "41", "51", "43", "44", "52", "46", "47", "48", "50",
]

REQUEST_DELAY = 2  # 요청 사이 딜레이(초)
PER_PAGE = 100     # 한 페이지당 매물 수 (최대 100)

# 농지은행 거래유형 코드 매핑 (원본 텍스트 → 코드)
BIZ_TYPE_MAP = {
    "맞춤형": {"매도": "D1", "임대": "D2"},
    "공공임대": {"매도": "B1", "임대": "B2"},
    "수탁": {"매도": "A1", "임대": "A2"},
    "경영회생": {"매도": "C1", "임대": "C2"},
}


def _resolve_biz_type_code(raw_text: str) -> str | None:
    """거래유형 원본 텍스트에서 코드(D1, B2 등) 추출
    예: '매도-맞춤형' → 'D1', '임대-공공임대' → 'B2'
    """
    trade = "임대" if "임대" in raw_text else "매도"
    for keyword, codes in BIZ_TYPE_MAP.items():
        if keyword in raw_text:
            return codes[trade]
    # 매핑 실패 시 대분류 기본값
    return "D1" if trade == "매도" else "D2"


def _build_url(sido_cd: str, sigun_cd: str = "", page_no: int = 1) -> str:
    """검색 GET URL 생성"""
    params = {
        "menuId": "020020",
        "schOk": "true",
        "schSidoCd": sido_cd,
        "schStat": "Y",            # 진행중
        "currentPageNo": page_no,
        "recordCountPerPage": PER_PAGE,
    }
    if sigun_cd:
        params["schSigunCd"] = sigun_cd
    return f"{FBO_BASE_URL}?{urlencode(params)}"


def _get_sigun_codes(page, sido_cd: str) -> list[str]:
    """시도 페이지에서 시군구 코드 목록 추출 (동적 로드)"""
    url = _build_url(sido_cd)
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1500)

    options = page.eval_on_selector_all(
        "select[name='schSigunCd'] option",
        "els => els.filter(o => o.value).map(o => o.value)",
    )
    return options


def _get_total_count(soup) -> int:
    """페이지에서 총 건수 추출"""
    total_el = soup.select_one(".ddfs_list_header .total-filter h3 span")
    return int(total_el.get_text(strip=True)) if total_el else 0


def crawl_listings() -> list[dict]:
    """전국 시도를 순회하며 농지은행 매물 전체 수집.
    한 시도의 총 건수가 PER_PAGE 이상이면 시군구별로 분할 크롤링.
    """
    results = []
    seen_keys: set[str] = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for sido_cd in SIDO_CODES:
            try:
                # 1차: 시도 전체 조회
                url = _build_url(sido_cd)
                page.goto(url, wait_until="networkidle", timeout=30000)
                page.wait_for_timeout(1500)

                html = page.content()
                soup = BeautifulSoup(html, "lxml")
                total_count = _get_total_count(soup)

                if total_count >= PER_PAGE:
                    # 100건 이상이면 시군구별 분할 크롤링
                    sigun_codes = page.eval_on_selector_all(
                        "select[name='schSigunCd'] option",
                        "els => els.filter(o => o.value).map(o => o.value)",
                    )
                    logger.info(
                        f"시도 {sido_cd}: {total_count}건 (≥{PER_PAGE}) → "
                        f"시군구 {len(sigun_codes)}개로 분할 크롤링"
                    )
                    sido_total = 0
                    for sigun_cd in sigun_codes:
                        try:
                            sigun_listings = _crawl_sido(
                                page, sido_cd, seen_keys, sigun_cd=sigun_cd
                            )
                            results.extend(sigun_listings)
                            sido_total += len(sigun_listings)
                        except Exception:
                            logger.exception(
                                f"시군구 {sigun_cd} 크롤링 실패"
                            )
                        time.sleep(REQUEST_DELAY)
                    logger.info(f"시도 {sido_cd}: 총 {sido_total}건 수집 (분할)")
                else:
                    # 100건 미만이면 현재 페이지에서 바로 파싱
                    sido_listings = _parse_page_listings(soup, seen_keys)
                    results.extend(sido_listings)
                    logger.info(f"시도 {sido_cd}: {len(sido_listings)}건 수집")

            except Exception:
                logger.exception(f"시도 {sido_cd} 크롤링 실패")

            time.sleep(REQUEST_DELAY)

        browser.close()

    logger.info(f"전국 총 {len(results)}건 수집 완료")
    return results


def _parse_page_listings(soup, seen_keys: set) -> list[dict]:
    """이미 로드된 BeautifulSoup 페이지에서 매물 목록 파싱"""
    listings: list[dict] = []

    table = soup.select_one("table.table-toggle")
    if not table:
        return listings

    rows = table.select("tbody tr")
    for row in rows:
        cols = row.select("td")
        if len(cols) < 9:
            continue
        listing = _parse_row(cols)
        if not listing:
            continue
        if listing["listing_key"] in seen_keys:
            continue
        seen_keys.add(listing["listing_key"])
        listings.append(listing)

    return listings


def _crawl_sido(page, sido_cd: str, seen_keys: set,
                sigun_cd: str = "") -> list[dict]:
    """한 시도(또는 시군구)의 전체 페이지를 수집"""
    listings: list[dict] = []
    page_no = 1

    while True:
        url = _build_url(sido_cd, sigun_cd=sigun_cd, page_no=page_no)
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)

        html = page.content()
        soup = BeautifulSoup(html, "lxml")

        # 총 건수 확인
        total_count = _get_total_count(soup)
        if total_count == 0:
            break

        # 매물 파싱
        page_listings = _parse_page_listings(soup, seen_keys)
        listings.extend(page_listings)

        # 다음 페이지 여부 판단
        if len(page_listings) == 0:
            break

        total_pages = (total_count + PER_PAGE - 1) // PER_PAGE
        if page_no >= total_pages:
            break

        page_no += 1
        time.sleep(REQUEST_DELAY)

    return listings


def _parse_row(cols) -> dict | None:
    """테이블 행 파싱 — 컬럼 순서: 구분/소재지/지목/필지수/총면적/희망가/신청기한/신청자/신청"""
    try:
        text = [col.get_text(strip=True) for col in cols]

        # 0: 구분 (매도-맞춤형, 임대-공공임대 등)
        trade_type_raw = text[0]
        trade_type = "임대" if "임대" in trade_type_raw else "매도"
        biz_type_code = _resolve_biz_type_code(trade_type_raw)

        # 1: 농지 소재지 — 링크에서 listing_key 추출
        address_full = text[1]
        link = cols[1].select_one("a")
        if not link:
            return None

        listing_key = _extract_listing_key(link)
        if not listing_key:
            return None

        # 2: 지목 (전/답/과수원)
        land_category_raw = text[2]
        land_category = "기타"
        for cat in ("전", "답", "과수원"):
            if cat in land_category_raw:
                land_category = cat
                break

        # 3: 필지수
        parcel_count = _parse_int(text[3])

        # 4: 총면적 (㎡) — 소수점 포함 (예: '4,000.0')
        total_area_sqm = _parse_area(text[4])

        # 5: 희망가 (원)
        price = _parse_int(text[5])

        # 6: 신청기한 (예: '2026.04.15', '2026-04-15', '2026/04/15')
        deadline = _parse_deadline(text[6]) if len(text) > 6 else None

        # 7: 신청자 수
        applicant_count = _parse_int(text[7]) if len(text) > 7 else None

        # price_per_sqm 계산
        price_per_sqm = None
        if price and total_area_sqm and total_area_sqm > 0:
            price_per_sqm = price // total_area_sqm

        return {
            "listing_key": listing_key,
            "trade_type": trade_type,
            "biz_type": biz_type_code,
            "biz_type_raw": trade_type_raw,
            "land_category": land_category,
            "address_full": address_full,
            "parcel_count": parcel_count,
            "total_area_sqm": total_area_sqm,
            "detail_url": f"https://www.fbo.or.kr/fsle/trde/TrdeDetail.do?reqFlndid={listing_key}",
            "price": price,
            "price_per_sqm": price_per_sqm,
            "deadline": deadline,
            "applicant_count": applicant_count,
        }
    except (IndexError, ValueError):
        return None


def _extract_listing_key(link) -> str | None:
    """a 태그에서 listing_key 추출 (onclick 또는 href)"""
    onclick = link.get("onclick", "")
    href = link.get("href", "")

    # onclick="fn_detail('XXXX')" 등의 패턴
    for pattern in [
        r"reqFlndid['\"]?\s*[:=]\s*['\"]?(\w+)",
        r"flndid['\"]?\s*[:=]\s*['\"]?(\w+)",
        r"fn_detail\s*\(\s*['\"](\w+)['\"]",
        r"goDetail\s*\(\s*['\"](\w+)['\"]",
        r"['\"](\w{10,})['\"]",  # 긴 ID 문자열
    ]:
        match = re.search(pattern, onclick, re.IGNORECASE)
        if match:
            return match.group(1)

    # href에서 추출
    match = re.search(r"reqFlndid=(\w+)", href)
    if match:
        return match.group(1)

    return None


def _parse_deadline(text: str) -> date | None:
    """마감일 문자열 → date 객체 변환
    농지은행 날짜 형식: '2026.04.15', '2026-04-15', '2026/04/15' 등
    """
    if not text or text.strip() in ("", "-", "없음", "미정", "상시"):
        return None
    cleaned = text.strip()
    for fmt in ("%Y.%m.%d", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d.", "%Y년 %m월 %d일"):
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            continue
    # 숫자만 추출해서 시도 (20260415 → 2026-04-15)
    digits = re.sub(r"[^\d]", "", cleaned)
    if len(digits) == 8:
        try:
            return datetime.strptime(digits, "%Y%m%d").date()
        except ValueError:
            pass
    logger.warning("마감일 파싱 실패: '%s'", text)
    return None


def _parse_int(text: str) -> int | None:
    """숫자 문자열 파싱 (콤마 제거)"""
    cleaned = re.sub(r"[^\d]", "", text)
    return int(cleaned) if cleaned else None


def _parse_area(text: str) -> int | None:
    """면적 문자열 파싱 — 소수점 포함 (예: '4,000.0' → 4000)
    농지은행은 면적을 소수점 한 자리까지 표시하므로 float로 파싱 후 반올림"""
    cleaned = re.sub(r"[^\d.]", "", text)
    if not cleaned:
        return None
    try:
        return round(float(cleaned))
    except ValueError:
        return None
