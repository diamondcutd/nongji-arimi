import os
import uuid
import httpx
from datetime import datetime, timezone
from urllib.parse import urlencode

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from app.schemas import UserResponse, Token
from app.auth_utils import create_access_token, get_current_user

router = APIRouter()

DATABASE_URL   = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nongji")
KAKAO_REST_KEY    = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
KAKAO_REDIRECT    = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:8000/auth/kakao/callback")
FRONTEND_URL      = os.getenv("FRONTEND_URL", "http://localhost:8000")


def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


# ── 카카오 로그인 ──────────────────────────────────────────────────────────────

@router.get("/kakao/login")
def kakao_login():
    """카카오 인가 URL로 리다이렉트"""
    if not KAKAO_REST_KEY:
        raise HTTPException(status_code=500, detail="KAKAO_REST_API_KEY 환경변수가 설정되지 않았습니다")
    params = urlencode({
        "client_id":     KAKAO_REST_KEY,
        "redirect_uri":  KAKAO_REDIRECT,
        "response_type": "code",
    })
    return RedirectResponse(f"https://kauth.kakao.com/oauth/authorize?{params}")


@router.get("/kakao/callback")
async def kakao_callback(code: str, conn=Depends(get_conn)):
    """카카오 인가 코드 → 액세스 토큰 → 사용자 정보 → JWT 발급"""
    # 1) 인가 코드 → 액세스 토큰
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type":    "authorization_code",
                "client_id":     KAKAO_REST_KEY,
                "client_secret": KAKAO_CLIENT_SECRET,
                "redirect_uri":  KAKAO_REDIRECT,
                "code":          code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if token_res.status_code != 200:
            import logging
            logging.getLogger(__name__).error("카카오 토큰 실패: %s %s", token_res.status_code, token_res.text)
            raise HTTPException(status_code=400, detail=f"카카오 토큰 발급 실패: {token_res.text}")
        access_token = token_res.json()["access_token"]

        # 2) 액세스 토큰 → 사용자 정보
        user_res = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_res.status_code != 200:
            raise HTTPException(status_code=400, detail="카카오 사용자 정보 조회 실패")
        kakao_data = user_res.json()

    kakao_id = str(kakao_data["id"])
    kakao_account = kakao_data.get("kakao_account", {})
    nickname = (
        kakao_account.get("profile", {}).get("nickname")
        or kakao_data.get("properties", {}).get("nickname")
    )
    email = kakao_account.get("email")  # 선택 동의 — 없을 수 있음

    # 3) DB upsert (kakao_id 기준)
    cur = conn.cursor()
    try:
        now = datetime.now(timezone.utc)

        # 기존 사용자 확인
        cur.execute("SELECT id FROM users WHERE kakao_id = %s", (kakao_id,))
        row = cur.fetchone()

        if row:
            # 기존 사용자 — last_login 갱신, 닉네임/이메일 최신화
            user_id = str(row["id"])
            cur.execute(
                """
                UPDATE users
                SET last_login = %s,
                    nickname   = COALESCE(%s, nickname),
                    email      = COALESCE(%s, email),
                    is_active  = TRUE
                WHERE kakao_id = %s
                """,
                (now, nickname, email, kakao_id),
            )
        else:
            # 신규 사용자
            user_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO users (id, kakao_id, email, nickname, plan, is_active, created_at, last_login)
                VALUES (%s, %s, %s, %s, 'free', TRUE, %s, %s)
                """,
                (user_id, kakao_id, email, nickname, now, now),
            )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"사용자 처리 중 오류: {e}")
    finally:
        cur.close()

    # 4) JWT 발급 → 프론트엔드로 리다이렉트
    jwt_token = create_access_token(user_id)
    return RedirectResponse(f"{FRONTEND_URL}/dashboard?token={jwt_token}")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.patch("/me/deactivate")
def deactivate_account(current_user=Depends(get_current_user), conn=Depends(get_conn)):
    """계정 휴면 처리
    - is_active=FALSE → 로그인 차단, 매칭 제외
    - 알림 조건 비활성화 (재로그인 시 복구 가능하도록 데이터 보존)
    - 재로그인 시 is_active=TRUE로 복구 필요 (별도 복구 API 또는 로그인 시 자동 복구)
    """
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE users SET is_active = FALSE WHERE id = %s RETURNING id",
            (current_user["id"],),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
        # 알림 조건 비활성화 (데이터는 보존)
        cur.execute(
            "UPDATE alert_conditions SET is_active = FALSE WHERE user_id = %s",
            (current_user["id"],),
        )
        conn.commit()
        return {"message": "계정이 휴면 처리되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"휴면 처리 중 오류: {e}")
    finally:
        cur.close()


@router.delete("/me")
def delete_account(current_user=Depends(get_current_user), conn=Depends(get_conn)):
    """계정 탈퇴 — 개인정보 완전 정리
    처리 순서:
    1. notifications 삭제 (발송 이력 — 개인정보 포함)
    2. alert_conditions 삭제 (알림 조건)
    3. user_contexts 삭제 (단기 기억)
    4. subscriptions 삭제 (구독 정보)
    5. users 익명화 (email/password/nickname/phone 제거, is_active=FALSE)
       → 완전 DELETE 대신 익명화하는 이유:
         - chat_messages FK가 SET NULL이라 메시지 보존 가능
         - 같은 이메일로 재가입 허용 (email이 변경되므로 UNIQUE 충돌 없음)
         - 통계용 user row 보존 (가입자 수 추이 등)
    """
    cur = conn.cursor()
    try:
        user_id = current_user["id"]

        # 1) 관련 데이터 삭제 (FK CASCADE와 무관하게 명시적으로)
        cur.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM alert_conditions WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM user_contexts WHERE user_id = %s", (user_id,))
        cur.execute("DELETE FROM subscriptions WHERE user_id = %s", (user_id,))

        # 2) 개인정보 익명화
        cur.execute(
            """UPDATE users
               SET email = 'withdrawn_' || LEFT(id::text, 8) || '@deleted',
                   password_hash = '',
                   nickname = NULL,
                   phone = NULL,
                   kakao_id = NULL,
                   kakao_channel_user_key = NULL,
                   is_active = FALSE
               WHERE id = %s RETURNING id""",
            (user_id,),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

        conn.commit()
        return {"message": "계정이 탈퇴 처리되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"탈퇴 처리 중 오류: {e}")
    finally:
        cur.close()
