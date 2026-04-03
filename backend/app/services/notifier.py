"""
알림 발송 서비스
이메일(SendGrid), 카카오 알림톡, SMS(솔라피) 지원
"""
import os
import logging
from datetime import datetime

from app.database import async_session
from app.models import Notification, User, Listing, AlertCondition

logger = logging.getLogger(__name__)


def format_price(price: int | None) -> str:
    """금액 포맷팅: 100000000 → '1억', 50000000 → '5,000만'"""
    if price is None:
        return "미정"
    if price >= 100_000_000:
        eok = price // 100_000_000
        remainder = (price % 100_000_000) // 10_000
        if remainder > 0:
            return f"{eok}억 {remainder:,}만원"
        return f"{eok}억원"
    elif price >= 10_000:
        return f"{price // 10_000:,}만원"
    return f"{price:,}원"


def format_area(area: int | None) -> str:
    """면적 포맷팅: ㎡ + 평"""
    if area is None:
        return "미정"
    pyeong = round(area / 3.3058, 1)
    return f"{area:,}㎡ ({pyeong:,}평)"


def build_email_html(user: User, matches: list[dict]) -> str:
    """이메일 HTML 본문 생성"""
    condition_name = matches[0]["condition"].name or "알림 조건"
    count = len(matches)

    listings_html = ""
    for m in matches:
        listing: Listing = m["listing"]
        listings_html += f"""
        <div style="border:1px solid #e0e0e0; border-radius:8px; padding:16px; margin-bottom:12px;">
            <p style="font-size:16px; font-weight:bold; margin:0 0 8px;">
                📍 {listing.address or '주소 미상'}
            </p>
            <p style="margin:4px 0;">📋 지목: {listing.land_category or '-'} | 면적: {format_area(listing.total_area)}</p>
            <p style="margin:4px 0;">💰 희망가: {format_price(listing.price)}</p>
            <p style="margin:4px 0;">📅 신청기한: {listing.deadline or '-'}</p>
            <p style="margin:4px 0;">👥 현재 신청자: {listing.applicant_count or 0}명</p>
            {'<a href="' + listing.detail_url + '" style="display:inline-block; margin-top:8px; padding:8px 16px; background:#2E7D32; color:white; border-radius:4px; text-decoration:none;">신청하러 가기 →</a>' if listing.detail_url else ''}
        </div>
        """

    return f"""
    <div style="max-width:600px; margin:0 auto; font-family:'Noto Sans KR', sans-serif;">
        <div style="background:#2E7D32; color:white; padding:20px; border-radius:8px 8px 0 0;">
            <h1 style="margin:0; font-size:20px;">🌾 농지알리미</h1>
        </div>
        <div style="padding:20px; background:#fff;">
            <p>안녕하세요 <strong>{user.email}</strong>님,</p>
            <p>설정하신 조건 "<strong>{condition_name}</strong>"에 맞는 매물이 <strong>{count}건</strong> 등록됐습니다.</p>
            <hr style="border:none; border-top:1px solid #eee; margin:16px 0;">
            {listings_html}
            <p style="color:#666; font-size:13px; margin-top:20px;">
                농지은행에서 바로 확인하세요.<br>
                이 알림은 농지알리미에서 발송되었습니다.
            </p>
        </div>
    </div>
    """


def build_kakao_message(matches: list[dict]) -> str:
    """카카오 알림톡 메시지 생성"""
    condition_name = matches[0]["condition"].name or "알림 조건"
    count = len(matches)

    msg = f"[농지알리미] 관심 농지 매물 알림\n\n"
    msg += f"{condition_name}에 맞는 매물 {count}건이 등록됐습니다.\n\n"

    for m in matches[:3]:  # 알림톡은 글자수 제한이 있으므로 최대 3건
        listing: Listing = m["listing"]
        msg += f"📍 {listing.address or '-'} ({listing.land_category or '-'})\n"
        msg += f"📐 {format_area(listing.total_area)} / 💰 {format_price(listing.price)}\n"
        msg += f"📅 신청기한: {listing.deadline or '-'}\n\n"

    if count > 3:
        msg += f"외 {count - 3}건 더 있습니다.\n\n"

    msg += "▶ 농지은행에서 신청하기"
    return msg


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """SendGrid로 이메일 발송"""
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SENDGRID_FROM_EMAIL", "noreply@nongji-alert.com")

    if not api_key:
        logger.warning("SENDGRID_API_KEY 미설정, 이메일 발송 건너뜀")
        return False

    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        message = Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
        )
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        logger.info(f"이메일 발송 성공: {to_email} (status: {response.status_code})")
        return response.status_code in (200, 201, 202)
    except Exception as e:
        logger.error(f"이메일 발송 실패: {to_email} - {e}")
        return False


async def send_kakao(kakao_id: str, message: str) -> bool:
    """
    카카오 알림톡 발송
    카카오 비즈메시지 API (알림톡) 사용
    사전 준비: 카카오 비즈니스 채널 등록 + 알림톡 템플릿 승인 필요
    """
    api_key = os.getenv("KAKAO_API_KEY")
    template_id = os.getenv("KAKAO_TEMPLATE_ID")

    if not api_key or not template_id:
        logger.warning("카카오 API 키 미설정, 알림톡 발송 건너뜀")
        return False

    try:
        import httpx

        # 카카오 알림톡 API (비즈메시지)
        # 실제 운영 시 카카오 비즈메시지 발송 대행사(NHN Cloud, 솔라피 등)를 통해 발송
        # 여기서는 솔라피의 카카오 알림톡 API를 사용하는 예시
        solapi_key = os.getenv("SOLAPI_API_KEY")
        solapi_secret = os.getenv("SOLAPI_API_SECRET")
        pfid = os.getenv("KAKAO_PFID", "")  # 카카오 채널 ID

        if solapi_key and solapi_secret:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.solapi.com/messages/v4/send",
                    json={
                        "message": {
                            "to": kakao_id,  # 수신자 전화번호
                            "from": os.getenv("SOLAPI_FROM_PHONE", ""),
                            "kakaoOptions": {
                                "pfId": pfid,
                                "templateId": template_id,
                                "variables": {},
                            },
                            "text": message,
                            "type": "ATA",  # 알림톡
                        }
                    },
                    headers={
                        "Authorization": f"Bearer {solapi_key}",
                    },
                )
                success = response.status_code == 200
                if success:
                    logger.info(f"카카오 알림톡 발송 성공: {kakao_id}")
                else:
                    logger.error(f"카카오 알림톡 발송 실패: {kakao_id} - {response.text}")
                return success
        else:
            logger.warning("솔라피 API 키 미설정, 카카오 알림톡 발송 건너뜀")
            return False

    except Exception as e:
        logger.error(f"카카오 알림톡 발송 오류: {kakao_id} - {e}")
        return False


async def send_sms(phone: str, message: str) -> bool:
    """솔라피 SMS 발송"""
    api_key = os.getenv("SOLAPI_API_KEY")
    api_secret = os.getenv("SOLAPI_API_SECRET")
    from_phone = os.getenv("SOLAPI_FROM_PHONE")

    if not api_key or not api_secret:
        logger.warning("솔라피 API 키 미설정, SMS 발송 건너뜀")
        return False

    try:
        import httpx

        # 솔라피 v4 API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.solapi.com/messages/v4/send",
                json={
                    "message": {
                        "to": phone,
                        "from": from_phone,
                        "text": message[:90],  # SMS 90바이트 제한
                        "type": "SMS",
                    }
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                },
            )
            success = response.status_code == 200
            if success:
                logger.info(f"SMS 발송 성공: {phone}")
            else:
                logger.error(f"SMS 발송 실패: {phone} - {response.text}")
            return success
    except Exception as e:
        logger.error(f"SMS 발송 오류: {phone} - {e}")
        return False


async def record_notification(
    user_id: str, listing_id: str, condition_id: str, channel: str, success: bool
):
    """알림 발송 이력 DB 저장"""
    async with async_session() as session:
        notification = Notification(
            user_id=user_id,
            listing_id=listing_id,
            condition_id=condition_id,
            channel=channel,
            status="sent" if success else "failed",
        )
        session.add(notification)
        await session.commit()


async def notify_matches(matches: list[dict]):
    """
    매칭 결과에 대해 알림 발송
    - Basic: 이메일만
    - Premium: 이메일 + 카카오 + SMS
    """
    # 사용자별로 그룹핑
    user_matches: dict[str, list[dict]] = {}
    for m in matches:
        uid = m["user"].id
        if uid not in user_matches:
            user_matches[uid] = []
        user_matches[uid].append(m)

    for user_id, user_match_list in user_matches.items():
        user: User = user_match_list[0]["user"]
        condition: AlertCondition = user_match_list[0]["condition"]

        # 조건별로 다시 그룹핑
        cond_matches: dict[str, list[dict]] = {}
        for m in user_match_list:
            cid = m["condition"].id
            if cid not in cond_matches:
                cond_matches[cid] = []
            cond_matches[cid].append(m)

        for cond_id, cond_match_list in cond_matches.items():
            count = len(cond_match_list)
            cond_name = cond_match_list[0]["condition"].name or "알림 조건"

            # 1) 이메일 (Basic + Premium)
            if user.email:
                subject = f"[농지알리미] 관심 지역에 새 매물이 등록됐어요! ({count}건)"
                html = build_email_html(user, cond_match_list)
                success = await send_email(user.email, subject, html)

                for m in cond_match_list:
                    await record_notification(
                        user.id, m["listing"].id, m["condition"].id, "email", success
                    )

            # 2) 카카오 + SMS (Premium만)
            if user.plan == "premium":
                kakao_msg = build_kakao_message(cond_match_list)

                if user.kakao_id:
                    success = await send_kakao(user.kakao_id, kakao_msg)
                    for m in cond_match_list:
                        await record_notification(
                            user.id, m["listing"].id, m["condition"].id, "kakao", success
                        )

                if user.phone:
                    sms_text = f"[농지알리미] {cond_name}에 맞는 매물 {count}건 등록. 앱에서 확인하세요."
                    success = await send_sms(user.phone, sms_text)
                    for m in cond_match_list:
                        await record_notification(
                            user.id, m["listing"].id, m["condition"].id, "sms", success
                        )

    logger.info(f"알림 발송 완료: {len(user_matches)}명 대상")
