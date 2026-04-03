"""DB 연결 및 매물 저장 로직"""

import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/nongji")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def upsert_listing(conn, listing: dict):
    """매물 원장 upsert — listing_key 기준 중복 체크"""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO listings (
                listing_key, region_id, trade_type, biz_type,
                land_category, address_full, parcel_count,
                total_area_sqm, detail_url
            ) VALUES (
                %(listing_key)s, %(region_id)s, %(trade_type)s, %(biz_type)s,
                %(land_category)s, %(address_full)s, %(parcel_count)s,
                %(total_area_sqm)s, %(detail_url)s
            )
            ON CONFLICT (listing_key) DO UPDATE SET
                last_seen_at = NOW(),
                status = 'active',
                biz_type = EXCLUDED.biz_type
            RETURNING id, (xmax = 0) AS is_inserted
        """, listing)
        row = cur.fetchone()
        return row[0], row[1]  # listing_id, is_new


def insert_snapshot(conn, listing_id: str, snapshot: dict):
    """매물 스냅샷 저장 — 값이 변했을 때만 새 행 추가.

    비교 대상: price, price_per_sqm, applicant_count, deadline
    - 첫 스냅샷(is_first=True): 무조건 저장
    - 이후: 직전 스냅샷과 비교해 하나라도 변경되면 저장
    - 변경 없으면: 저장 안 함 (listings.last_seen_at만 갱신됨)

    Returns: True if snapshot was inserted, False if skipped
    """
    data = {**snapshot, "listing_id": listing_id}

    with conn.cursor() as cur:
        # 첫 스냅샷이면 무조건 저장
        if snapshot.get("is_first"):
            cur.execute("""
                INSERT INTO listing_snapshots (
                    listing_id, price, price_per_sqm,
                    applicant_count, deadline, is_first
                ) VALUES (
                    %(listing_id)s, %(price)s, %(price_per_sqm)s,
                    %(applicant_count)s, %(deadline)s, %(is_first)s
                )
            """, data)
            return True

        # 직전 스냅샷 조회
        cur.execute("""
            SELECT price, price_per_sqm, applicant_count, deadline
            FROM listing_snapshots
            WHERE listing_id = %(listing_id)s
            ORDER BY crawled_at DESC
            LIMIT 1
        """, data)
        prev = cur.fetchone()

        if prev is None:
            # 스냅샷이 아예 없으면 저장 (비정상 상태 복구)
            cur.execute("""
                INSERT INTO listing_snapshots (
                    listing_id, price, price_per_sqm,
                    applicant_count, deadline, is_first
                ) VALUES (
                    %(listing_id)s, %(price)s, %(price_per_sqm)s,
                    %(applicant_count)s, %(deadline)s, TRUE
                )
            """, data)
            return True

        # 변경 감지: 하나라도 다르면 새 스냅샷 저장
        prev_price, prev_ppsqm, prev_applicant, prev_deadline = prev
        changed = (
            snapshot.get("price") != prev_price
            or snapshot.get("price_per_sqm") != prev_ppsqm
            or snapshot.get("applicant_count") != prev_applicant
            or snapshot.get("deadline") != prev_deadline
        )

        if changed:
            cur.execute("""
                INSERT INTO listing_snapshots (
                    listing_id, price, price_per_sqm,
                    applicant_count, deadline, is_first
                ) VALUES (
                    %(listing_id)s, %(price)s, %(price_per_sqm)s,
                    %(applicant_count)s, %(deadline)s, FALSE
                )
            """, data)
            return True

        return False


def get_new_listings(conn):
    """알림 미발송 매물 조회"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT l.*, ls.price, ls.price_per_sqm, ls.applicant_count, ls.deadline
            FROM listings l
            JOIN listing_snapshots ls ON ls.listing_id = l.id AND ls.is_first = TRUE
            WHERE l.is_new = TRUE
            ORDER BY l.first_seen_at DESC
        """)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]


def mark_listings_notified(conn, listing_ids: list):
    """알림 발송 완료 표시"""
    if not listing_ids:
        return
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE listings SET is_new = FALSE WHERE id = ANY(%s)",
            (listing_ids,)
        )


def find_region_id(conn, address: str):
    """주소 문자열에서 region_id 찾기 — 시도→시군구→읍면동 계층적 매칭.

    주소 형식: '서울특별시 강남구 율현동 280'
    1단계: 주소의 첫 번째 토큰으로 시도(level=1) 매칭
    2단계: 시도 하위에서 두 번째 토큰으로 시군구(level=2) 매칭
    3단계: 시군구 하위에서 세 번째 토큰으로 읍면동(level=3) 매칭
    가장 하위 매칭 결과를 반환. 매칭 실패 시 상위 레벨이라도 반환.
    """
    if not address or not address.strip():
        return None

    parts = address.strip().split()
    if len(parts) < 2:
        return None

    with conn.cursor() as cur:
        # 1단계: 시도 매칭
        cur.execute(
            "SELECT id FROM regions WHERE level = 1 AND %s LIKE name || '%%'",
            (parts[0],),
        )
        row = cur.fetchone()
        if not row:
            return None
        sido_id = row[0]
        best_match = sido_id

        # 2단계: 시군구 매칭 (시도 하위)
        cur.execute(
            "SELECT id FROM regions WHERE level = 2 AND parent_id = %s AND name = %s",
            (sido_id, parts[1]),
        )
        row = cur.fetchone()
        if not row:
            return best_match
        sigun_id = row[0]
        best_match = sigun_id

        # 3단계: 읍면동 매칭 (시군구 하위)
        if len(parts) >= 3:
            cur.execute(
                "SELECT id FROM regions WHERE level = 3 AND parent_id = %s AND name = %s",
                (sigun_id, parts[2]),
            )
            row = cur.fetchone()
            if row:
                best_match = row[0]

        return best_match
