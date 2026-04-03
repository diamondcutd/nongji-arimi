"""
농지알리미 매칭 엔진 v3 — 누적 다이제스트 발송
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3섹션 구조:
  🔴 마감 임박 (D-7 이내) — 이전에 알린 매물 중 곧 마감되는 것
  🆕 오늘 새 매물        — 오늘 새로 매칭된 매물
  📋 놓친 매물           — 이전 7일간 알렸지만 아직 활성인 매물

인지심리학 적용:
  - 손실 회피: 마감 임박 섹션을 맨 위에 배치 + 붉은 강조
  - 자이가르닉 효과: "미확인 N건" 카운트로 열린 고리 유발
  - 청킹: 섹션별 그룹핑으로 인지 부하 감소
  - 초두 효과: 가장 중요한 정보를 맨 위에
"""

import asyncio
import json
import logging
import smtplib
import os
import uuid
from collections import defaultdict
from datetime import datetime, date, timedelta, UTC
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from dotenv import load_dotenv
from sqlalchemy import text

from app.database import async_session

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_FROM_NAME = os.getenv("ALERT_FROM_NAME", "알리미")

DEADLINE_WARN_DAYS = 7   # 마감 임박 기준 (D-7)
CATCHUP_DAYS = 7         # 놓친 매물 조회 기간 (최근 7일)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# DB 조회 헬퍼
# ---------------------------------------------------------------------------

async def fetch_new_listings(session) -> list[dict]:
    """신규 매물 + 최초 스냅샷 조회."""
    result = await session.execute(text("""
        SELECT l.id, l.listing_key, l.region_id, l.trade_type, l.biz_type,
               l.land_category, l.address_full, l.parcel_count,
               l.total_area_sqm, l.detail_url, l.first_seen_at,
               ls.price, ls.price_per_sqm, ls.applicant_count, ls.deadline
        FROM listings l
        JOIN listing_snapshots ls ON ls.listing_id = l.id AND ls.is_first = TRUE
        WHERE l.is_new = TRUE
        ORDER BY l.first_seen_at DESC
    """))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


async def fetch_active_conditions(session) -> list[dict]:
    """활성 알림 조건 + 사용자 이메일 조회."""
    result = await session.execute(text("""
        SELECT ac.id AS condition_id, ac.user_id, ac.region_id,
               ac.include_children, ac.land_category, ac.trade_type,
               ac.biz_type, ac.area_min, ac.area_max, ac.price_max,
               u.email, u.is_active AS user_active
        FROM alert_conditions ac
        JOIN users u ON u.id = ac.user_id
        WHERE ac.is_active = TRUE AND u.is_active = TRUE
    """))
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


async def fetch_region_with_ancestors(session, region_id: str) -> set[str]:
    """해당 region_id와 모든 상위 region_id 집합 반환."""
    ancestors: set[str] = set()
    current_id = region_id
    while current_id:
        ancestors.add(str(current_id))
        row = await session.execute(
            text("SELECT parent_id FROM regions WHERE id = :id"),
            {"id": current_id},
        )
        parent = row.scalar_one_or_none()
        current_id = str(parent) if parent else None
    return ancestors


async def fetch_already_notified(session, listing_ids: list[str]) -> set[tuple[str, str]]:
    """이미 발송된 (user_id, listing_id) 쌍 — 중복 방지."""
    if not listing_ids:
        return set()
    result = await session.execute(text("""
        SELECT CAST(user_id AS text), CAST(listing_id AS text)
        FROM notifications
        WHERE listing_id = ANY(:ids)
    """), {"ids": listing_ids})
    return {(row[0], row[1]) for row in result.fetchall()}


async def fetch_catchup_listings(session, user_id: str, days: int = CATCHUP_DAYS) -> list[dict]:
    """
    놓친 매물 조회 — 최근 N일 내 알림을 보냈지만 아직 활성인 매물.
    (오늘 새로 매칭된 것은 제외)
    """
    today = date.today()
    cutoff_date = today - timedelta(days=days)
    result = await session.execute(text("""
        SELECT DISTINCT l.id, l.listing_key, l.region_id, l.trade_type, l.biz_type,
               l.land_category, l.address_full, l.parcel_count,
               l.total_area_sqm, l.detail_url, l.first_seen_at,
               ls.price, ls.price_per_sqm, ls.applicant_count, ls.deadline,
               n.sent_at
        FROM notifications n
        JOIN listings l ON l.id = n.listing_id
        JOIN listing_snapshots ls ON ls.listing_id = l.id AND ls.is_first = TRUE
        WHERE n.user_id = CAST(:user_id AS uuid)
          AND n.status = 'sent'
          AND n.sent_at >= :cutoff_date
          AND n.sent_at < :today
          AND l.status = 'active'
        ORDER BY ls.deadline ASC NULLS LAST, n.sent_at DESC
    """), {"user_id": user_id, "cutoff_date": cutoff_date, "today": today})
    columns = result.keys()
    return [dict(zip(columns, row)) for row in result.fetchall()]


# ---------------------------------------------------------------------------
# 매칭 로직
# ---------------------------------------------------------------------------

async def matches_region(session, condition: dict, listing: dict,
                         region_cache: dict[str, set[str]]) -> bool:
    """지역 매칭."""
    cond_region = condition["region_id"]
    if cond_region is None:
        return True
    listing_region = listing["region_id"]
    if listing_region is None:
        return False
    cond_region_str = str(cond_region)
    listing_region_str = str(listing_region)
    if cond_region_str == listing_region_str:
        return True
    if not condition["include_children"]:
        return False
    if listing_region_str not in region_cache:
        region_cache[listing_region_str] = await fetch_region_with_ancestors(
            session, listing_region_str
        )
    return cond_region_str in region_cache[listing_region_str]


BIZ_TO_TRADE = {
    "D1": "매도", "A1": "매도", "B1": "매도", "C1": "매도",
    "D2": "임대", "A2": "임대", "B2": "임대", "C2": "임대",
}
BIZ_NAMES = {
    "D1": "매도-맞춤형", "A1": "매도-수탁", "B1": "매도-공공임대", "C1": "매도-경영회생",
    "D2": "임대-맞춤형", "A2": "임대-수탁", "B2": "임대-공공임대", "C2": "임대-경영회생",
}


def _parse_biz_type(value) -> list[str]:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except (json.JSONDecodeError, TypeError):
            return []
    return []


def matches_fields(condition: dict, listing: dict) -> bool:
    """지역 외 필드 매칭."""
    if condition["land_category"] is not None:
        if condition["land_category"] != listing["land_category"]:
            return False

    cond_biz = _parse_biz_type(condition.get("biz_type"))
    listing_biz = listing.get("biz_type")
    listing_trade = listing.get("trade_type")

    if cond_biz:
        if listing_biz is not None:
            if listing_biz not in cond_biz:
                return False
        else:
            cond_trades = set(BIZ_TO_TRADE.get(b) for b in cond_biz if b in BIZ_TO_TRADE)
            if listing_trade not in cond_trades:
                return False
    elif condition.get("trade_type") is not None:
        if condition["trade_type"] != listing_trade:
            return False

    area = listing["total_area_sqm"]
    if area is not None:
        if condition["area_min"] is not None and area < condition["area_min"]:
            return False
        if condition["area_max"] is not None and area > condition["area_max"]:
            return False

    price = listing.get("price")
    if price is not None:
        if condition["price_max"] is not None and price > condition["price_max"]:
            return False

    return True


# ---------------------------------------------------------------------------
# 섹션 분류
# ---------------------------------------------------------------------------

def classify_listings(
    new_listings: list[dict],
    catchup_listings: list[dict],
) -> dict[str, list[dict]]:
    """
    매물을 3개 섹션으로 분류.
    - urgent:  마감 D-7 이내 (new + catchup 통합)
    - new:     오늘 새 매물 (urgent에 포함된 것 제외)
    - catchup: 놓친 매물 (urgent에 포함된 것 제외)
    """
    today = date.today()
    deadline_cutoff = today + timedelta(days=DEADLINE_WARN_DAYS)

    urgent = []
    new_normal = []
    catchup_normal = []

    seen_ids = set()

    # 새 매물 중 마감 임박 분리
    for l in new_listings:
        lid = str(l["id"])
        dl = l.get("deadline")
        if dl is not None and dl <= deadline_cutoff:
            if lid not in seen_ids:
                l["_days_left"] = (dl - today).days
                urgent.append(l)
                seen_ids.add(lid)
        else:
            if lid not in seen_ids:
                new_normal.append(l)
                seen_ids.add(lid)

    # 놓친 매물 중 마감 임박 분리
    for l in catchup_listings:
        lid = str(l["id"])
        if lid in seen_ids:
            continue
        dl = l.get("deadline")
        if dl is not None and dl <= deadline_cutoff:
            l["_days_left"] = (dl - today).days
            urgent.append(l)
            seen_ids.add(lid)
        else:
            catchup_normal.append(l)
            seen_ids.add(lid)

    # 마감 임박은 마감일 가까운 순
    urgent.sort(key=lambda x: x.get("_days_left", 999))

    return {
        "urgent": urgent,
        "new": new_normal,
        "catchup": catchup_normal,
    }


# ---------------------------------------------------------------------------
# 다이제스트 이메일 HTML 빌드
# ---------------------------------------------------------------------------

LAND_NAMES = {"전": "전 (밭)", "답": "답 (논)", "과수원": "과수원", "기타": "기타"}

# ---------------------------------------------------------------------------
# fbo.or.kr 지역 코드 매핑 (TrdeDetail.do 세션 차단 → TrdeList.do 시군구 필터링)
# ---------------------------------------------------------------------------
FBO_SIDO_MAP = {
    "서울특별시": "11", "부산광역시": "26", "대구광역시": "27",
    "인천광역시": "28", "광주광역시": "29", "대전광역시": "30",
    "울산광역시": "31", "세종특별자치시": "36", "경기도": "41",
    "강원특별자치도": "51", "충청북도": "43", "충청남도": "44",
    "전북특별자치도": "52", "전라남도": "46", "경상북도": "47",
    "경상남도": "48", "제주특별자치도": "50",
    "강원도": "51", "전라북도": "52",  # 구 명칭 호환
}

# 시도코드 → { 시군구이름: fbo시군구코드 }  (fbo.or.kr에서 수집)
FBO_SIGUN_MAP: dict[str, dict[str, str]] = {
    "11": {  # 서울
        "종로구": "11110", "중구": "11140", "용산구": "11170", "성동구": "11200",
        "광진구": "11215", "동대문구": "11230", "중랑구": "11260", "성북구": "11290",
        "강북구": "11305", "도봉구": "11320", "노원구": "11350", "은평구": "11380",
        "서대문구": "11410", "마포구": "11440", "양천구": "11470", "강서구": "11500",
        "구로구": "11530", "금천구": "11545", "영등포구": "11560", "동작구": "11590",
        "관악구": "11620", "서초구": "11650", "강남구": "11680", "송파구": "11710",
        "강동구": "11740",
    },
    "26": {  # 부산
        "중구": "26110", "서구": "26140", "동구": "26170", "영도구": "26200",
        "부산진구": "26230", "동래구": "26260", "남구": "26290", "북구": "26320",
        "해운대구": "26350", "사하구": "26380", "금정구": "26410", "강서구": "26440",
        "연제구": "26470", "수영구": "26500", "사상구": "26530", "기장군": "26710",
    },
    "27": {  # 대구
        "중구": "27110", "동구": "27140", "서구": "27170", "남구": "27200",
        "북구": "27230", "수성구": "27260", "달서구": "27290", "달성군": "27710",
        "군위군": "27720",
    },
    "28": {  # 인천
        "중구": "28110", "동구": "28140", "미추홀구": "28177", "연수구": "28185",
        "남동구": "28200", "부평구": "28237", "계양구": "28245", "서구": "28260",
        "강화군": "28710", "옹진군": "28720",
    },
    "29": {  # 광주
        "동구": "29110", "서구": "29140", "남구": "29155", "북구": "29170",
        "광산구": "29200",
    },
    "30": {  # 대전
        "동구": "30110", "중구": "30140", "서구": "30170", "유성구": "30200",
        "대덕구": "30230",
    },
    "31": {  # 울산
        "중구": "31110", "남구": "31140", "동구": "31170", "북구": "31200",
        "울주군": "31710",
    },
    "36": {  # 세종
        "세종시": "36110",
    },
    "41": {  # 경기
        "수원시": "41110", "성남시": "41130", "의정부시": "41150",
        "안양시": "41170", "부천시": "41190", "광명시": "41210",
        "평택시": "41220", "동두천시": "41250", "안산시": "41270",
        "고양시": "41280", "과천시": "41290", "구리시": "41310",
        "남양주시": "41360", "오산시": "41370", "시흥시": "41390",
        "군포시": "41410", "의왕시": "41430", "하남시": "41450",
        "용인시": "41460", "파주시": "41480", "이천시": "41500",
        "안성시": "41550", "김포시": "41570", "광주시": "41610",
        "양주시": "41630", "포천시": "41650", "여주시": "41670",
        "연천군": "41800", "가평군": "41820", "양평군": "41830",
    },
    "51": {  # 강원
        "춘천시": "51110", "원주시": "51130", "강릉시": "51150",
        "동해시": "51170", "태백시": "51190", "속초시": "51210",
        "삼척시": "51230", "홍천군": "51720", "횡성군": "51730",
        "영월군": "51750", "평창군": "51760", "정선군": "51770",
        "철원군": "51780", "화천군": "51790", "양구군": "51800",
        "인제군": "51810", "고성군": "51820", "양양군": "51830",
    },
    "43": {  # 충북
        "청주시": "43110", "충주시": "43130", "제천시": "43150",
        "보은군": "43720", "옥천군": "43730", "영동군": "43740",
        "증평군": "43745", "진천군": "43750", "괴산군": "43760",
        "음성군": "43770", "단양군": "43800",
    },
    "44": {  # 충남
        "천안시": "44130", "공주시": "44150", "보령시": "44180",
        "아산시": "44200", "서산시": "44210", "논산시": "44230",
        "계룡시": "44250", "당진시": "44270", "금산군": "44710",
        "부여군": "44760", "서천군": "44770", "청양군": "44790",
        "홍성군": "44800", "예산군": "44810", "태안군": "44825",
    },
    "52": {  # 전북
        "전주시": "52110", "군산시": "52130", "익산시": "52140",
        "정읍시": "52180", "남원시": "52190", "김제시": "52210",
        "완주군": "52710", "진안군": "52720", "무주군": "52730",
        "장수군": "52740", "임실군": "52750", "순창군": "52770",
        "고창군": "52790", "부안군": "52800",
    },
    "46": {  # 전남
        "목포시": "46110", "여수시": "46130", "순천시": "46150",
        "나주시": "46170", "광양시": "46230", "담양군": "46710",
        "곡성군": "46720", "구례군": "46730", "고흥군": "46770",
        "보성군": "46780", "화순군": "46790", "장흥군": "46800",
        "강진군": "46810", "해남군": "46820", "영암군": "46830",
        "무안군": "46840", "함평군": "46860", "영광군": "46870",
        "장성군": "46880", "완도군": "46890", "진도군": "46900",
        "신안군": "46910",
    },
    "47": {  # 경북
        "포항시": "47110", "경주시": "47130", "김천시": "47150",
        "안동시": "47170", "구미시": "47190", "영주시": "47210",
        "영천시": "47230", "상주시": "47250", "문경시": "47280",
        "경산시": "47290", "의성군": "47730", "청송군": "47750",
        "영양군": "47760", "영덕군": "47770", "청도군": "47820",
        "고령군": "47830", "성주군": "47840", "칠곡군": "47850",
        "예천군": "47900", "봉화군": "47920", "울진군": "47930",
        "울릉군": "47940",
    },
    "48": {  # 경남
        "창원시": "48120", "진주시": "48170", "통영시": "48220",
        "사천시": "48240", "김해시": "48250", "밀양시": "48270",
        "거제시": "48310", "양산시": "48330", "의령군": "48720",
        "함안군": "48730", "창녕군": "48740", "고성군": "48820",
        "남해군": "48840", "하동군": "48850", "산청군": "48860",
        "함양군": "48870", "거창군": "48880", "합천군": "48890",
    },
    "50": {  # 제주
        "제주시": "50110", "서귀포시": "50130",
    },
}


def _build_fbo_list_url(address: str) -> str:
    """주소에서 시도+시군구를 추출하여 fbo.or.kr 목록 페이지 URL 생성.

    TrdeDetail.do는 세션 없이 접근 불가하므로 TrdeList.do로 대체.
    시군구까지 필터링하여 사용자가 해당 매물을 빠르게 찾을 수 있도록 함.
    """
    if not address:
        return "https://www.fbo.or.kr"

    # 1) 시도 코드 찾기
    fbo_sido = None
    for sido_name, code in FBO_SIDO_MAP.items():
        if sido_name in address:
            fbo_sido = code
            break
    if not fbo_sido:
        return "https://www.fbo.or.kr"

    base = (f"https://www.fbo.or.kr/fsle/trde/TrdeList.do"
            f"?menuId=020020&schOk=true&schSidoCd={fbo_sido}&schStat=Y")

    # 2) 시군구 코드 찾기 (주소 토큰에서 시/군/구 이름 매칭)
    sigun_map = FBO_SIGUN_MAP.get(fbo_sido, {})
    if sigun_map:
        parts = address.split()
        # 주소 2번째 토큰이 시군구 (예: "전북특별자치도 군산시 성산면 ...")
        for part in parts[1:3]:  # 2~3번째 토큰 확인
            if part in sigun_map:
                return base + f"&schSigunCd={sigun_map[part]}"
            # "시" "군" "구"로 끝나는 토큰 부분 매칭
            for name, code in sigun_map.items():
                if name in part or part in name:
                    return base + f"&schSigunCd={code}"

    return base


def _format_area(area: int | None) -> str:
    if area is None:
        return "-"
    pyeong = round(area / 3.3058)
    return f"{area:,}㎡ ({pyeong:,}평)"


def _format_price(price: int | None) -> str:
    """가격 포맷 — DB에는 원(won) 단위로 저장됨"""
    if price is None:
        return "-"
    man = price / 10000  # 원 → 만원
    if man >= 10000:
        eok = int(man) // 10000
        r = int(man) % 10000
        return f"{eok}억 {r:,}만원" if r else f"{eok}억원"
    if man >= 1:
        return f"{int(man):,}만원"
    return f"{price:,}원"


def _deadline_badge(listing: dict) -> str:
    """마감일 뱃지 — 손실 회피 심리 적용."""
    dl = listing.get("deadline")
    days_left = listing.get("_days_left")
    if dl is None:
        return ""
    if days_left is not None and days_left <= 3:
        color = "#dc3545"  # 빨강
        label = f"D-{days_left}" if days_left > 0 else "오늘 마감"
    elif days_left is not None and days_left <= 7:
        color = "#e67e22"  # 주황
        label = f"D-{days_left}"
    else:
        return ""
    return f'<span style="display:inline-block;background-color:{color};color:#fff;font-size:10px;font-weight:700;padding:3px 8px;border-radius:12px;margin-left:6px;">{label}</span>'


def _build_card(listing: dict, index: int, is_urgent: bool = False) -> str:
    """개별 매물 카드."""
    location = listing["address_full"] or "위치 정보 없음"
    biz_code = listing.get("biz_type") or ""
    biz_label = BIZ_NAMES.get(biz_code, listing.get("trade_type") or "")
    land_label = LAND_NAMES.get(listing.get("land_category") or "", listing.get("land_category") or "-")
    detail_url = _build_fbo_list_url(listing["address_full"] or "")
    dl_badge = _deadline_badge(listing)

    # 마감 임박 카드는 붉은 테두리
    border = "2px solid #dc3545" if is_urgent else "1px solid #e9ecef"
    bg = "#fff5f5" if is_urgent else ("#ffffff" if index % 2 == 0 else "#f8faf8")

    return f"""
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:{bg};border:{border};border-radius:10px;margin-bottom:10px;">
          <tr><td style="padding:14px 18px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td>
                  <span style="display:inline-block;background-color:#2d6a4f;color:#fff;font-size:10px;font-weight:700;padding:3px 8px;border-radius:12px;margin-right:4px;">{biz_label}</span>
                  <span style="display:inline-block;background-color:#e9ecef;color:#555;font-size:10px;font-weight:600;padding:3px 8px;border-radius:12px;">{land_label}</span>
                  {dl_badge}
                </td>
                <td align="right">
                  <a href="{detail_url}" target="_blank" style="color:#2d6a4f;font-size:12px;font-weight:700;text-decoration:none;">상세보기 &rarr;</a>
                </td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:6px;">
                  <div style="color:#1b4332;font-size:14px;font-weight:700;line-height:1.4;">{location}</div>
                </td>
              </tr>
              <tr>
                <td colspan="2" style="padding-top:6px;">
                  <span style="color:#6c757d;font-size:11px;">면적</span>
                  <span style="color:#333;font-size:13px;font-weight:600;margin-right:14px;"> {_format_area(listing["total_area_sqm"])}</span>
                  <span style="color:#6c757d;font-size:11px;">가격</span>
                  <span style="color:#2d6a4f;font-size:13px;font-weight:600;margin-right:14px;"> {_format_price(listing.get("price"))}</span>
                  <span style="color:#6c757d;font-size:11px;">마감</span>
                  <span style="color:#333;font-size:13px;font-weight:600;"> {listing.get("deadline") or "-"}</span>
                </td>
              </tr>
            </table>
          </td></tr>
        </table>"""


def _build_section(title: str, emoji: str, listings: list[dict],
                   color: str, description: str, is_urgent: bool = False) -> str:
    """섹션 HTML — 제목 + 설명 + 카드 목록."""
    if not listings:
        return ""
    cards = "\n".join(_build_card(l, i, is_urgent) for i, l in enumerate(listings))
    return f"""
    <tr>
      <td style="padding:16px 24px 4px;">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td>
              <span style="font-size:18px;vertical-align:middle;">{emoji}</span>
              <span style="color:{color};font-size:15px;font-weight:700;vertical-align:middle;margin-left:4px;">{title}</span>
              <span style="color:#999;font-size:12px;vertical-align:middle;margin-left:8px;">{len(listings)}건</span>
            </td>
          </tr>
          <tr>
            <td style="padding:4px 0 10px;">
              <span style="color:#888;font-size:11px;">{description}</span>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="padding:0 24px 8px;">
        {cards}
      </td>
    </tr>"""


def build_digest_html(sections: dict[str, list[dict]]) -> str:
    """3섹션 누적 다이제스트 HTML."""
    now_str = datetime.now().strftime("%Y년 %m월 %d일")
    urgent = sections["urgent"]
    new = sections["new"]
    catchup = sections["catchup"]

    total = len(urgent) + len(new) + len(catchup)

    # ── 요약 배너 텍스트 (자이가르닉 효과: 숫자로 미완결 유발) ──
    summary_parts = []
    if urgent:
        summary_parts.append(f'<span style="color:#dc3545;font-weight:700;">마감 임박 {len(urgent)}건</span>')
    if new:
        summary_parts.append(f'신규 {len(new)}건')
    if catchup:
        summary_parts.append(f'<span style="color:#e67e22;">미확인 {len(catchup)}건</span>')
    summary_text = " &middot; ".join(summary_parts)

    # ── 각 섹션 빌드 ──
    urgent_html = _build_section(
        "마감 임박", "🔴", urgent, "#dc3545",
        "곧 마감되는 매물이에요. 놓치면 아까워요!",
        is_urgent=True,
    )
    new_html = _build_section(
        "오늘 새 매물", "🆕", new, "#2d6a4f",
        "오늘 새로 올라온 매물이에요.",
    )
    catchup_html = _build_section(
        "놓친 매물", "📋", catchup, "#e67e22",
        "아직 확인하지 않은 매물이에요. 여전히 신청 가능해요.",
    )

    return f"""\
<!DOCTYPE html>
<html lang="ko">
<head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /></head>
<body style="margin:0;padding:0;background-color:#f5f5f0;font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f0;padding:28px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

  <!-- 헤더 -->
  <tr>
    <td style="background:linear-gradient(135deg,#2d6a4f,#40916c);padding:24px 28px;text-align:center;">
      <div style="font-size:28px;margin-bottom:4px;">🌾</div>
      <h1 style="margin:0;color:#ffffff;font-size:18px;font-weight:700;">농지알리미</h1>
      <p style="margin:4px 0 0;color:#b7e4c7;font-size:12px;">{now_str}</p>
    </td>
  </tr>

  <!-- 요약 배너 — 손실 회피 + 자이가르닉 효과 -->
  <tr>
    <td style="padding:16px 24px 4px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#d8f3dc;border-radius:10px;">
        <tr><td style="padding:12px 16px;text-align:center;">
          <span style="color:#1b4332;font-size:14px;font-weight:700;">총 {total}건</span>
          <span style="color:#52796f;font-size:12px;margin-left:6px;">{summary_text}</span>
        </td></tr>
      </table>
    </td>
  </tr>

  <!-- 섹션들 (초두 효과: 마감 임박 → 신규 → 놓친 매물) -->
{urgent_html}
{new_html}
{catchup_html}

  <!-- 푸터 -->
  <tr>
    <td style="padding:16px 24px 20px;text-align:center;border-top:1px solid #eee;">
      <p style="margin:0 0 8px;color:#999;font-size:11px;">조건을 변경하려면 대시보드에서 수정해주세요.</p>
      <p style="margin:0;color:#bbb;font-size:10px;">&copy; 2026 농지알리미 &middot; 이 메일은 자동 발송되었습니다.</p>
    </td>
  </tr>

</table>
</td></tr></table>
</body></html>"""


def send_digest_email(to_email: str, sections: dict[str, list[dict]]) -> bool:
    """다이제스트 메일 발송."""
    urgent_count = len(sections["urgent"])
    new_count = len(sections["new"])
    catchup_count = len(sections["catchup"])
    total = urgent_count + new_count + catchup_count

    # 제목 — 손실 회피 심리: 마감 임박이 있으면 강조
    if urgent_count > 0:
        subject = f"🔴 마감 임박 {urgent_count}건 포함! 농지알리미 새 매물 총 {total}건"
    elif catchup_count > 0:
        subject = f"🌾 새 매물 {new_count}건 + 미확인 {catchup_count}건이 기다리고 있어요"
    else:
        subject = f"🌾 농지알리미 — 새 매물 {new_count}건을 찾았어요!"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((ALERT_FROM_NAME, GMAIL_USER))
        msg["To"] = to_email
        msg.attach(MIMEText(build_digest_html(sections), "html", "utf-8"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        logger.info("다이제스트 발송 → %s (긴급%d 신규%d 놓침%d)",
                     to_email, urgent_count, new_count, catchup_count)
        return True
    except Exception:
        logger.exception("다이제스트 발송 실패 → %s", to_email)
        return False


# ---------------------------------------------------------------------------
# 메인 매칭 실행
# ---------------------------------------------------------------------------

async def run_matcher():
    """신규 매물 매칭 + 누적 매물 수집 → 3섹션 다이제스트 발송."""
    async with async_session() as session:
        # 1) 신규 매물 조회
        new_listings = await fetch_new_listings(session)
        logger.info("신규 매물 %d건", len(new_listings))

        # 2) 활성 알림 조건 조회
        conditions = await fetch_active_conditions(session)
        if not conditions:
            logger.info("활성 알림 조건 없음 — 종료")
            return

        logger.info("활성 알림 조건 %d건 로드", len(conditions))

        # 3) 중복 방지용 기발송 목록
        listing_ids = [str(l["id"]) for l in new_listings]
        already_notified = await fetch_already_notified(session, listing_ids)

        # 4) 신규 매물 매칭 — 사용자별 그룹핑
        region_cache: dict[str, set[str]] = {}
        # { user_id: { email, new_matches: [{listing, condition_id}] } }
        user_data: dict[str, dict] = {}

        for listing in new_listings:
            listing_id = str(listing["id"])
            seen_users: set[str] = set()

            for cond in conditions:
                user_id = str(cond["user_id"])
                if user_id in seen_users:
                    continue
                if (user_id, listing_id) in already_notified:
                    continue
                if not await matches_region(session, cond, listing, region_cache):
                    continue
                if not matches_fields(cond, listing):
                    continue

                if user_id not in user_data:
                    user_data[user_id] = {"email": cond["email"], "new_matches": []}
                user_data[user_id]["new_matches"].append({
                    "listing": listing,
                    "listing_id": listing_id,
                    "condition_id": str(cond["condition_id"]),
                })
                seen_users.add(user_id)

        # 5) 각 사용자별 놓친 매물(catchup) 조회 + 3섹션 분류 + 발송
        # 새 매칭이 없는 사용자라도 놓친 매물이 있을 수 있으므로
        # 조건이 있는 모든 사용자 대상으로 확인
        all_user_ids = set(str(c["user_id"]) for c in conditions)
        all_user_emails = {str(c["user_id"]): c["email"] for c in conditions}

        sent_users = 0
        sent_new_total = 0

        for user_id in all_user_ids:
            email = all_user_emails[user_id]
            new_matches = user_data.get(user_id, {}).get("new_matches", [])
            new_listings_for_user = [m["listing"] for m in new_matches]

            # 놓친 매물 조회 + 현재 조건으로 재검증
            catchup_raw = await fetch_catchup_listings(session, user_id)
            user_conditions = [c for c in conditions if str(c["user_id"]) == user_id]
            catchup = []
            for cl in catchup_raw:
                for uc in user_conditions:
                    if await matches_region(session, uc, cl, region_cache) and matches_fields(uc, cl):
                        catchup.append(cl)
                        break

            # 새 매물도 없고 놓친 매물도 없으면 스킵
            if not new_listings_for_user and not catchup:
                continue

            # 3섹션 분류
            sections = classify_listings(new_listings_for_user, catchup)

            # 전체가 비어있으면 스킵
            total = len(sections["urgent"]) + len(sections["new"]) + len(sections["catchup"])
            if total == 0:
                continue

            # 발송
            success = send_digest_email(email, sections)
            status = "sent" if success else "failed"
            # asyncpg는 naive datetime 필요 (DB가 TIMESTAMP, TIMESTAMPTZ 아님)
            now = datetime.now(UTC).replace(tzinfo=None)

            # 새 매물에 대한 notification 기록 (놓친 매물은 이미 기록됨)
            for m in new_matches:
                await session.execute(text("""
                    INSERT INTO notifications (id, user_id, listing_id, condition_id, channel, status, sent_at)
                    VALUES (:id, :uid, :lid, :cid, :ch, :st, :at)
                """), {
                    "id": str(uuid.uuid4()),
                    "uid": user_id,
                    "lid": m["listing_id"],
                    "cid": m["condition_id"],
                    "ch": "email",
                    "st": status,
                    "at": now,
                })

            if success:
                sent_users += 1
                sent_new_total += len(new_matches)

        # 6) is_new 해제
        if listing_ids:
            await session.execute(
                text("UPDATE listings SET is_new = FALSE WHERE id = ANY(:ids)"),
                {"ids": listing_ids},
            )

        await session.commit()
        logger.info("발송 완료: %d명, 신규 %d건 알림", sent_users, sent_new_total)


if __name__ == "__main__":
    asyncio.run(run_matcher())
