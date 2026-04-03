import os
from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Subscription
from app.schemas import CheckoutRequest, SubscriptionResponse
from app.auth_utils import get_current_user

router = APIRouter()

PLAN_PRICES = {"basic": 9900, "premium": 19900}


@router.get("/me", response_model=SubscriptionResponse | None)
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription)
        .where(
            Subscription.user_id == current_user.id,
            Subscription.status == "active",
        )
        .order_by(Subscription.created_at.desc())
    )
    return result.scalar_one_or_none()


@router.post("/checkout")
async def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    if data.plan not in PLAN_PRICES:
        raise HTTPException(status_code=400, detail="유효하지 않은 플랜입니다")

    client_key = os.getenv("TOSS_CLIENT_KEY")
    if not client_key:
        raise HTTPException(status_code=500, detail="결제 설정이 완료되지 않았습니다")

    amount = PLAN_PRICES[data.plan]
    order_id = f"NONGJI-{current_user.id[:8]}-{int(datetime.now(UTC).timestamp())}"

    return {
        "clientKey": client_key,
        "orderId": order_id,
        "amount": amount,
        "orderName": f"농지알리미 {data.plan.title()} 월 구독",
        "customerEmail": current_user.email,
    }


@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """토스페이먼츠 결제 완료 웹훅"""
    import httpx

    body = await request.json()
    payment_key = body.get("paymentKey")
    order_id = body.get("orderId")
    amount = body.get("amount")

    secret_key = os.getenv("TOSS_SECRET_KEY")
    if not secret_key:
        raise HTTPException(status_code=500, detail="결제 설정 오류")

    # 토스페이먼츠 결제 승인 API 호출
    import base64
    auth = base64.b64encode(f"{secret_key}:".encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            json={"paymentKey": payment_key, "orderId": order_id, "amount": amount},
            headers={"Authorization": f"Basic {auth}"},
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="결제 승인 실패")

    payment_data = response.json()

    # orderId에서 user_id 추출
    # orderId 형식: NONGJI-{user_id[:8]}-{timestamp}
    parts = order_id.split("-")
    if len(parts) < 3:
        raise HTTPException(status_code=400, detail="잘못된 주문 ID")

    user_id_prefix = parts[1]

    # 사용자 찾기
    result = await db.execute(
        select(User).where(User.id.startswith(user_id_prefix))
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    # 플랜 결정 (금액 기반)
    plan = "premium" if amount >= 19900 else "basic"

    # 기존 활성 구독 만료 처리
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user.id,
            Subscription.status == "active",
        )
    )
    for sub in result.scalars().all():
        sub.status = "expired"

    # 새 구독 생성
    subscription = Subscription(
        user_id=user.id,
        plan=plan,
        status="active",
        started_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(days=30),
        payment_key=payment_key,
    )
    db.add(subscription)

    # 사용자 플랜 업데이트
    user.plan = plan
    await db.commit()

    return {"status": "success", "plan": plan}
