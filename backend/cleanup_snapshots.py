"""중복 스냅샷 정리 스크립트.

같은 매물(listing_id)에서 price, price_per_sqm, applicant_count, deadline이
모두 동일한 스냅샷 중 가장 오래된 것만 남기고 나머지를 삭제.
is_first=TRUE인 스냅샷은 절대 삭제하지 않음.
"""

import logging
from crawler.db import get_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def cleanup():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 정리 전 현황
            cur.execute("SELECT COUNT(*) FROM listing_snapshots")
            before = cur.fetchone()[0]
            logger.info("정리 전 스냅샷: %d건", before)

            # 중복 스냅샷 삭제 (is_first=TRUE는 보호)
            cur.execute("""
                DELETE FROM listing_snapshots
                WHERE id IN (
                    SELECT id FROM (
                        SELECT
                            id,
                            is_first,
                            ROW_NUMBER() OVER (
                                PARTITION BY listing_id, price, price_per_sqm,
                                             applicant_count, deadline
                                ORDER BY crawled_at ASC
                            ) AS rn
                        FROM listing_snapshots
                    ) ranked
                    WHERE rn > 1 AND is_first = FALSE
                )
            """)
            deleted = cur.rowcount
            logger.info("삭제된 중복 스냅샷: %d건", deleted)

            # 정리 후 현황
            cur.execute("SELECT COUNT(*) FROM listing_snapshots")
            after = cur.fetchone()[0]
            logger.info("정리 후 스냅샷: %d건 (%.1f%% 절약)", after, (1 - after / before) * 100)

            conn.commit()

    except Exception:
        conn.rollback()
        logger.exception("정리 실패")
    finally:
        conn.close()


if __name__ == "__main__":
    cleanup()
