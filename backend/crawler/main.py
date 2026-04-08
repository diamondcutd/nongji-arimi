"""농지알리미 크롤러 메인 — APScheduler로 매일 2회 실행"""

import asyncio
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from crawler.scraper import crawl_listings
from crawler.db import (
    get_connection,
    upsert_listing,
    insert_snapshot,
    find_region_id,
    expire_unseen_listings,
)
from matcher import run_matcher

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def crawl_and_notify():
    """크롤링 → DB 저장 → (추후) 알림 발송"""
    logger.info("크롤링 시작")

    try:
        listings = crawl_listings()
        logger.info(f"수집 매물: {len(listings)}건")

        if not listings:
            logger.warning("수집된 매물 없음")
            return

        conn = get_connection()
        new_count = 0
        changed_count = 0
        seen_keys = []

        try:
            for item in listings:
                # 주소에서 region_id 매칭
                region_id = find_region_id(conn, item.get("address_full", ""))

                listing_data = {
                    "listing_key": item["listing_key"],
                    "region_id": region_id,
                    "trade_type": item["trade_type"],
                    "biz_type": item.get("biz_type"),
                    "land_category": item["land_category"],
                    "address_full": item["address_full"],
                    "parcel_count": item.get("parcel_count"),
                    "total_area_sqm": item["total_area_sqm"],
                    "detail_url": item["detail_url"],
                }

                listing_id, is_new = upsert_listing(conn, listing_data)
                seen_keys.append(item["listing_key"])

                snapshot_data = {
                    "price": item.get("price"),
                    "price_per_sqm": item.get("price_per_sqm"),
                    "applicant_count": item.get("applicant_count") or 0,
                    "deadline": item.get("deadline"),
                    "is_first": is_new,
                }
                was_inserted = insert_snapshot(conn, listing_id, snapshot_data)

                if is_new:
                    new_count += 1
                elif was_inserted:
                    changed_count += 1

            # 농지은행에서 사라진 매물 만료 처리
            expired_count = expire_unseen_listings(conn, seen_keys)
            if expired_count > 0:
                logger.info("만료 처리: %d건 (농지은행에서 내려간 매물)", expired_count)

            conn.commit()
            unchanged = len(listings) - new_count - changed_count
            logger.info(
                "저장 완료 — 신규: %d건, 변경: %d건, 변동없음: %d건 (스냅샷 생략)",
                new_count, changed_count, unchanged,
            )

            # 매칭 → 이메일 발송 → is_new 해제
            if new_count > 0:
                logger.info("매칭 엔진 실행 시작")
                asyncio.run(run_matcher())
                logger.info("매칭 엔진 실행 완료")

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    except Exception:
        logger.exception("크롤링 실패")


def main():
    """스케줄러 시작 — 매일 오전 10시, 오후 5시 실행"""
    scheduler = BlockingScheduler()

    # 매일 오전 10시 — 농지은행 매물 등록 주기 맞춤
    scheduler.add_job(crawl_and_notify, "cron", hour=10, minute=0, id="morning_crawl")
    # 매일 오후 5시 — 수시 등록 매물 추가 수집
    scheduler.add_job(crawl_and_notify, "cron", hour=17, minute=0, id="evening_crawl")

    logger.info("스케줄러 시작 — 매일 10:00 / 17:00 크롤링")

    # 시작 시 1회 즉시 실행
    crawl_and_notify()

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("스케줄러 종료")


if __name__ == "__main__":
    main()
