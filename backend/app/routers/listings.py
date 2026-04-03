from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Listing
from app.schemas import ListingResponse
from app.auth_utils import get_current_user

router = APIRouter()


@router.get("", response_model=list[ListingResponse])
async def list_listings(
    sido_cd: str | None = None,
    sigun_cd: str | None = None,
    land_category: str | None = None,
    trade_type: str | None = None,
    area_min: int | None = None,
    area_max: int | None = None,
    price_min: int | None = None,
    price_max: int | None = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Listing).order_by(Listing.crawled_at.desc())

    if sido_cd:
        query = query.where(Listing.sido_cd == sido_cd)
    if sigun_cd:
        query = query.where(Listing.sigun_cd == sigun_cd)
    if land_category:
        query = query.where(Listing.land_category == land_category)
    if trade_type:
        query = query.where(Listing.trade_type.contains(trade_type))
    if area_min is not None:
        query = query.where(Listing.total_area >= area_min)
    if area_max is not None:
        query = query.where(Listing.total_area <= area_max)
    if price_min is not None:
        query = query.where(Listing.price >= price_min)
    if price_max is not None:
        query = query.where(Listing.price <= price_max)

    # Basic: 7일, Premium: 90일
    from datetime import datetime, timedelta, timezone
    if current_user.plan == "basic":
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    else:
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    query = query.where(Listing.crawled_at >= cutoff)

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{listing_id}", response_model=ListingResponse)
async def get_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException
    result = await db.execute(select(Listing).where(Listing.id == listing_id))
    listing = result.scalar_one_or_none()
    if not listing:
        raise HTTPException(status_code=404, detail="매물을 찾을 수 없습니다")
    return listing
