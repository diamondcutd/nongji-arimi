"""JWT 인증 유틸리티 — hashlib.sha256 + salt 방식"""
import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import psycopg2
import psycopg2.extras
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET 환경변수가 설정되지 않았습니다. .env 파일을 확인하세요.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7일
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/nongji")

bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """salt(32hex) + '$' + sha256(salt+password)(64hex) = 97자"""
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return f"{salt}${h}"


def verify_password(plain: str, stored: str) -> bool:
    """저장된 'salt$hash' 형식과 비교"""
    if "$" not in stored:
        return False
    salt, stored_hash = stored.split("$", 1)
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return secrets.compare_digest(h, stored_hash)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": user_id, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db_connection_exception = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="데이터베이스 연결 실패. 잠시 후 다시 시도해주세요",
    )

    try:
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    except psycopg2.Error as e:
        raise db_connection_exception

    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, email, nickname, phone, plan, is_active, created_at FROM users WHERE id = %s",
            (user_id,),
        )
        user = cur.fetchone()
        cur.close()
    except psycopg2.Error:
        raise db_connection_exception
    finally:
        conn.close()

    if user is None or not user["is_active"]:
        raise credentials_exception

    # id를 문자열로 변환 (UUID → str)
    user["id"] = str(user["id"])
    return user
