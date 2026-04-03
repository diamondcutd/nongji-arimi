from pydantic import BaseModel, EmailStr
from datetime import datetime, date


# ── Auth ──
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str | None = None
    phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    nickname: str | None
    plan: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Alert Conditions ──
class ConditionCreate(BaseModel):
    label: str | None = None
    region_id: str | None = None
    include_children: bool = True
    land_category: str | None = None
    trade_type: str | None = None
    biz_type: list[str] | None = None
    area_min: int | None = None
    area_max: int | None = None
    price_max: int | None = None
    notify_channels: list[str] | None = None
    created_via: str = "web"


class ConditionUpdate(BaseModel):
    label: str | None = None
    region_id: str | None = None
    include_children: bool | None = None
    land_category: str | None = None
    trade_type: str | None = None
    biz_type: list[str] | None = None
    area_min: int | None = None
    area_max: int | None = None
    price_max: int | None = None
    notify_channels: list[str] | None = None
    is_active: bool | None = None


class ConditionResponse(BaseModel):
    id: str
    user_id: str
    label: str | None = None
    region_id: str | None = None
    include_children: bool | None = None
    land_category: str | None = None
    trade_type: str | None = None
    biz_type: list | None = None
    area_min: int | None = None
    area_max: int | None = None
    price_max: int | None = None
    notify_channels: list | None = None
    created_via: str | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Listings ──
class ListingResponse(BaseModel):
    id: str
    listing_key: str
    trade_type: str | None
    biz_type: str | None
    address: str | None
    sido_cd: str | None
    sigun_cd: str | None
    eupmyeondong: str | None
    land_category: str | None
    parcel_count: int | None
    total_area: int | None
    total_area_pyeong: float | None = None
    price: int | None
    deadline: date | None
    applicant_count: int | None
    detail_url: str | None
    crawled_at: datetime

    model_config = {"from_attributes": True}

    def model_post_init(self, __context):
        if self.total_area is not None and self.total_area_pyeong is None:
            object.__setattr__(self, "total_area_pyeong", round(self.total_area / 3.3058, 1))


# ── Subscriptions ──
class CheckoutRequest(BaseModel):
    plan: str  # 'basic' | 'premium'


class SubscriptionResponse(BaseModel):
    id: str
    plan: str
    status: str
    started_at: datetime | None
    expires_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Listings query params ──
class ListingFilter(BaseModel):
    sido_cd: str | None = None
    sigun_cd: str | None = None
    land_category: str | None = None
    trade_type: str | None = None
    area_min: int | None = None
    area_max: int | None = None
    price_min: int | None = None
    price_max: int | None = None
    page: int = 1
    size: int = 20
