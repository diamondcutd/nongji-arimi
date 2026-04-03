import uuid
from datetime import datetime, date, timezone
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, Date, DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    kakao_id: Mapped[str | None] = mapped_column(String(50), unique=True)
    kakao_channel_user_key: Mapped[str | None] = mapped_column(String(100))
    chatbot_activated_at: Mapped[datetime | None] = mapped_column(DateTime)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    nickname: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    plan: Mapped[str] = mapped_column(String(20), default="free")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_login: Mapped[datetime | None] = mapped_column(DateTime)

    conditions: Mapped[list["AlertCondition"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")


class AlertCondition(Base):
    __tablename__ = "alert_conditions"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str | None] = mapped_column(String(100))
    sido_cd: Mapped[str | None] = mapped_column(String(10))
    sigun_cd: Mapped[str | None] = mapped_column(String(10))
    eupmyeondong: Mapped[str | None] = mapped_column(String(50))
    area_min: Mapped[int | None] = mapped_column(Integer)
    area_max: Mapped[int | None] = mapped_column(Integer)
    price_min: Mapped[int | None] = mapped_column(BigInteger)
    price_max: Mapped[int | None] = mapped_column(BigInteger)
    land_category: Mapped[str | None] = mapped_column(String(20))
    trade_type: Mapped[str | None] = mapped_column(String(20))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="conditions")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    listing_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    trade_type: Mapped[str | None] = mapped_column(String(20))
    biz_type: Mapped[str | None] = mapped_column(String(30))
    address: Mapped[str | None] = mapped_column(String(255))
    sido_cd: Mapped[str | None] = mapped_column(String(10))
    sigun_cd: Mapped[str | None] = mapped_column(String(10))
    eupmyeondong: Mapped[str | None] = mapped_column(String(50))
    land_category: Mapped[str | None] = mapped_column(String(20))
    parcel_count: Mapped[int | None] = mapped_column(Integer)
    total_area: Mapped[int | None] = mapped_column(Integer)
    price: Mapped[int | None] = mapped_column(BigInteger)
    deadline: Mapped[date | None] = mapped_column(Date)
    applicant_count: Mapped[int | None] = mapped_column(Integer)
    detail_url: Mapped[str | None] = mapped_column(String(500))
    crawled_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_new: Mapped[bool] = mapped_column(Boolean, default=True)

    notifications: Mapped[list["Notification"]] = relationship(back_populates="listing")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), ForeignKey("users.id"))
    listing_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), ForeignKey("listings.id"))
    condition_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), ForeignKey("alert_conditions.id"))
    channel: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20), default="sent")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="notifications")
    listing: Mapped["Listing"] = relationship(back_populates="notifications")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=False), ForeignKey("users.id"))
    plan: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    payment_key: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="subscriptions")
