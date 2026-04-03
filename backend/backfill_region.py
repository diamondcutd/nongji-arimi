"""기존 매물 1,345건의 region_id 백필 스크립트.

find_region_id() 개선 버전(계층적 매칭)을 사용하여
address_full → 시도 → 시군구 → 읍면동 순서로 정확한 region_id를 채움.
"""

import logging
from crawler.db import get_connection, find_region_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def backfill():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # region_id가 NULL인 매물 조회
            cur.execute("SELECT id, address_full FROM listings WHERE region_id IS NULL")
            rows = cur.fetchall()
            logger.info("백필 대상: %d건", len(rows))

            updated = 0
            failed = 0
            level_stats = {"sido": 0, "sigun": 0, "eupmyeon": 0}

            for listing_id, address in rows:
                region_id = find_region_id(conn, address)
                if region_id:
                    cur.execute(
                        "UPDATE listings SET region_id = %s WHERE id = %s",
                        (region_id, listing_id),
                    )
                    # 매칭 레벨 확인
                    cur.execute("SELECT level FROM regions WHERE id = %s", (region_id,))
                    level = cur.fetchone()[0]
                    if level == 1:
                        level_stats["sido"] += 1
                    elif level == 2:
                        level_stats["sigun"] += 1
                    else:
                        level_stats["eupmyeon"] += 1
                    updated += 1
                else:
                    failed += 1
                    if failed <= 10:
                        logger.warning("매칭 실패: %s", address)

            conn.commit()
            logger.info(
                "백필 완료! 성공: %d건 (읍면동: %d, 시군구: %d, 시도: %d), 실패: %d건",
                updated, level_stats["eupmyeon"], level_stats["sigun"],
                level_stats["sido"], failed,
            )

    except Exception:
        conn.rollback()
        logger.exception("백필 실패")
    finally:
        conn.close()


if __name__ == "__main__":
    backfill()
