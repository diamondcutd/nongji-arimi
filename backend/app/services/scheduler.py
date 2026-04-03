"""
크롤링 + 알림 스케줄 관리
APScheduler를 사용하여 자동 실행
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services.crawler import crawl_listings, crawl_all_regions
from matcher import run_matcher

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def crawl_and_notify():
    """크롤링 → 매칭 → 이메일 발송 전체 파이프라인"""
    try:
        logger.info("=== 크롤링 + 알림 파이프라인 시작 ===")

        # 1. 전체 매물 크롤링
        new_listings = await crawl_listings()
        logger.info(f"크롤링 완료: 신규 매물 {len(new_listings)}건")

        if not new_listings:
            logger.info("신규 매물 없음, 파이프라인 종료")
            return

        # 2. 매칭 + 이메일 발송 + is_new 해제
        await run_matcher()

        logger.info("=== 파이프라인 완료 ===")

    except Exception as e:
        logger.error(f"파이프라인 오류: {e}", exc_info=True)


def start_scheduler():
    """스케줄러 시작"""
    # 매주 화요일 오전 9시 (농지은행 매물 등록일)
    scheduler.add_job(
        crawl_and_notify,
        CronTrigger(day_of_week="tue", hour=9, minute=0),
        id="weekly_crawl",
        name="주간 크롤링 (화요일 09:00)",
        replace_existing=True,
    )

    # 매일 오전 8시 (수시 등록 대비)
    scheduler.add_job(
        crawl_and_notify,
        CronTrigger(hour=8, minute=0),
        id="daily_crawl",
        name="일간 크롤링 (매일 08:00)",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("스케줄러 시작됨: 화요일 09:00 + 매일 08:00")


def stop_scheduler():
    """스케줄러 중지"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("스케줄러 중지됨")
