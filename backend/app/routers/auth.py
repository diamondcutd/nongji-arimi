import os
import uuid
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import UserCreate, LoginRequest, UserResponse, Token
from app.auth_utils import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nongji")


def get_conn():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        yield conn
    finally:
        conn.close()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, conn=Depends(get_conn)):
    cur = conn.cursor()
    try:
        # 이메일 중복 확인
        cur.execute("SELECT id FROM users WHERE email = %s", (data.email,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다")

        # INSERT — 실제 users 테이블 컬럼에 맞춤
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        cur.execute(
            """
            INSERT INTO users (id, email, password_hash, nickname, phone, plan, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, nickname, phone, plan, is_active, created_at
            """,
            (user_id, data.email, hash_password(data.password), data.nickname, data.phone, "free", True, now),
        )
        user = cur.fetchone()
        conn.commit()
        return user

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"회원가입 처리 중 오류: {e}")
    finally:
        cur.close()


@router.post("/login", response_model=Token)
def login(data: LoginRequest, conn=Depends(get_conn)):
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, password_hash FROM users WHERE email = %s AND is_active = true",
            (data.email,),
        )
        user = cur.fetchone()

        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다")

        # last_login 갱신
        cur.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.now(timezone.utc), user["id"]))
        conn.commit()

        return Token(access_token=create_access_token(str(user["id"])))

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"로그인 처리 중 오류: {e}")
    finally:
        cur.close()


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
