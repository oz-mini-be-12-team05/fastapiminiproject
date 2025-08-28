# app/api/core/security.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.api.core.config import settings




# ---------------------------------------------------------------------
# Auth header(Bearer) 파서
# ---------------------------------------------------------------------
bearer = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------
_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return _pwd_ctx.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd_ctx.verify(plain_password, hashed_password)

# ---------------------------------------------------------------------
# Email verification token (itsdangerous)
# ---------------------------------------------------------------------
_EMAIL_SALT = "email-verify"
_email_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)

def make_email_token(email: str) -> str:
    return _email_serializer.dumps(email, salt=_EMAIL_SALT)

def read_email_token(token: str, max_age_sec: int = 60 * 60 * 24) -> str:
    try:
        return _email_serializer.loads(token, salt=_EMAIL_SALT, max_age=max_age_sec)
    except SignatureExpired:
        raise HTTPException(status_code=400, detail="Verification token expired")
    except BadSignature:
        raise HTTPException(status_code=400, detail="Invalid verification token")

# ---------------------------------------------------------------------
# JWT helpers
#  - typ: "access" | "refresh"  (주의: 키 이름은 typ 로 통일)
#  - refresh 에 jti 포함(미션5: 블랙리스트용)
# ---------------------------------------------------------------------
def _exp_after_minutes(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)

def _exp_after_days(days: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)

def create_access_token(sub: str, minutes: Optional[int] = None) -> str:
    minutes = minutes or settings.ACCESS_TOKEN_MINUTES
    payload = {
        "sub": sub,
        "typ": "access",
        "jti": uuid.uuid4().hex,
        "exp": _exp_after_minutes(minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(sub: str, days: Optional[int] = None) -> str:
    days = days or settings.REFRESH_TOKEN_DAYS
    payload = {
        "sub": sub,
        "typ": "refresh",
        "jti": uuid.uuid4().hex,
        "exp": _exp_after_days(days),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("typ") != token_type:
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# ---------------------------------------------------------------------
# Cookie helpers
# ---------------------------------------------------------------------
def set_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    cookie_args = dict(httponly=True, secure=settings.COOKIE_SECURE, samesite="lax")
    if settings.COOKIE_DOMAIN:
        cookie_args["domain"] = settings.COOKIE_DOMAIN

    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=settings.ACCESS_TOKEN_MINUTES * 60,
        path="/",
        **cookie_args,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_DAYS * 24 * 3600,
        path="/",
        **cookie_args,
    )

def clear_auth_cookies(response) -> None:
    args = {"path": "/"}
    if settings.COOKIE_DOMAIN:
        args["domain"] = settings.COOKIE_DOMAIN
    response.delete_cookie("access_token", **args)
    response.delete_cookie("refresh_token", **args)

# ---------------------------------------------------------------------
# Current user dependency
#  - 헤더 Bearer 우선, 없으면 access_token 쿠키 사용
# ---------------------------------------------------------------------
# app/api/core/security.py  (기존 함수 교체)
async def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials = Depends(bearer),
):
    token = None
    if creds and creds.scheme.lower() == "bearer":
        token = creds.credentials
    elif (ck := request.cookies.get("access_token")):
        token = ck
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decode_token(token, token_type="access")

    # ⬇ access jti 블랙리스트 체크
    jti = payload.get("jti")
    from app.api.repositories.token_blacklist_repo import is_jti_blacklisted
    if not jti or await is_jti_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Token blacklisted")
    from app.api.repositories.user_repo import get_by_email
    email = payload.get("sub")
    user = await get_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# app/api/core/security.py
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt
# 여기서는 user_repo를 임포트하지 않습니다!

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

async def authenticate_user(email: str, password: str):
    # 🔽 순환 임포트 방지: 함수 내부에서 임포트
    from app.api.repositories.user_repo import get_by_email
    user = await get_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# (토큰 생성/검증 함수 등 다른 부분은 기존 그대로)

async def is_token_revoked(jti: str) -> bool:
    # 🔽 함수 내부 임포트
    from app.api.repositories.token_blacklist_repo import is_jti_blacklisted
    return await is_jti_blacklisted(jti)

