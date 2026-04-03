"""
매물-조건 매칭 서비스
신규 매물과 사용자 알림 조건을 비교하여 알림 대상을 결정
"""
import logging
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import async_session
from app.models import Listing, AlertCondition, User
from app.utils.filters import matches_condition

logger = logging.getLogger(__name__)


async def find_matches() -> list[dict]:
    """
    신규 매물(is_new=True)과 활성 알림 조건을 매칭하여
    알림 대상 목록을 반환

    Returns:
        list[dict]: [{"user": User, "listing": Listing, "condition": AlertCondition}, ...]
    """
    matches = []

    async with async_session() as session:
        # 1. 신규 매물 조회
        result = await session.execute(
            select(Listing).where(Listing.is_new == True)
        )
        new_listings = result.scalars().all()

        if not new_listings:
            logger.info("신규 매물 없음")
            return matches

        logger.info(f"신규 매물 {len(new_listings)}건 매칭 시작")

        # 2. 활성 알림 조건 조회 (사용자 정보 포함)
        result = await session.execute(
            select(AlertCondition)
            .options(selectinload(AlertCondition.user))
            .where(AlertCondition.is_active == True)
        )
        conditions = result.scalars().all()

        if not conditions:
            logger.info("활성 알림 조건 없음")
            return matches

        logger.info(f"활성 알림 조건 {len(conditions)}개 확인")

        # 3. 매물 × 조건 매칭
        for listing in new_listings:
            for condition in conditions:
                if not condition.user or not condition.user.is_active:
                    continue

                # Basic 플랜: 지역+지목만 필터링 (면적/금액 무시)
                if condition.user.plan == "basic":
                    basic_condition = AlertCondition(
                        sido_cd=condition.sido_cd,
                        sigun_cd=condition.sigun_cd,
                        eupmyeondong=condition.eupmyeondong,
                        land_category=condition.land_category,
                        trade_type=condition.trade_type,
                    )
                    if matches_condition(listing, basic_condition):
                        matches.append({
                            "user": condition.user,
                            "listing": listing,
                            "condition": condition,
                        })
                else:
                    # Premium: 전체 필터
                    if matches_condition(listing, condition):
                        matches.append({
                            "user": condition.user,
                            "listing": listing,
                            "condition": condition,
                        })

        logger.info(f"매칭 결과: {len(matches)}건")

    return matches


async def mark_listings_processed():
    """매칭 완료된 신규 매물의 is_new를 False로 업데이트"""
    async with async_session() as session:
        result = await session.execute(
            select(Listing).where(Listing.is_new == True)
        )
        listings = result.scalars().all()
        for listing in listings:
            listing.is_new = False
        await session.commit()
        logger.info(f"{len(listings)}건 매물 처리 완료 표시")
