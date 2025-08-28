# app/api/v1/auth/endpoints.py
from __future__ import annotations

from datetime import datetime, timezone
from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    Request,
    Depends,
    status,
    Query,
)

from app.api.schemas import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    MessageResponse,
    RefreshTokenRequest,
)
from app.api.repositories.user_repo import get_by_email, create_user
from app.api.repositories.token_blacklist_repo import (
    is_jti_blacklisted,
    blacklist_jti,
)
from app.api.core.security import (
    get_current_user,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    set_auth_cookies,
    clear_auth_cookies,
)
from app.api.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MessageResponse)
async def register(payload: SignupRequest):
    if await get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = get_password_hash(payload.password.get_secret_value())
    await create_user(email=payload.email, name=payload.name, hashed_password=hashed)
    return MessageResponse(message="registered")


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    as_cookie: bool = Query(False, description="쿠키로 access/refresh를 설정할지 여부"),
):
    user = await get_by_email(payload.email)
    if not user or not verify_password(payload.password.get_secret_value(), user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access = create_access_token(user.email)
    refresh = create_refresh_token(user.email)

    if as_cookie:
        set_auth_cookies(response, access, refresh)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    body: RefreshTokenRequest | None = None,
    as_cookie: bool = Query(False, description="쿠키 모드로 새 토큰 세팅"),
):
    token = body.refresh_token if body else request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    payload = decode_token(token, token_type="refresh")
    email: str | None = payload.get("sub")
    jti: str | None = payload.get("jti")
    exp: int | None = payload.get("exp")

    if not jti or not exp:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # 블랙리스트 확인
    if await is_jti_blacklisted(jti):
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    user = await get_by_email(email or "")
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # 토큰 회전
    new_access = create_access_token(email)          # type: ignore[arg-type]
    new_refresh = create_refresh_token(email)        # type: ignore[arg-type]

    # 방금 사용한 refresh는 블랙리스트에 등록
    expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    await blacklist_jti(jti, expires_at)

    if as_cookie:
        set_auth_cookies(response, new_access, new_refresh)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.ACCESS_TOKEN_MINUTES * 60,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, response: Response, user=Depends(get_current_user)):
    # 1) 쿠키의 refresh 블랙리스트
    if (rt := request.cookies.get("refresh_token")):
        try:
            p = decode_token(rt, token_type="refresh")
            if (jti := p.get("jti")) and (exp := p.get("exp")):
                await blacklist_jti(jti, datetime.fromtimestamp(exp, tz=timezone.utc))
        except Exception:
            pass

    # 2) (선택) 헤더의 access 블랙리스트
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        acc = auth.split(" ", 1)[1]
        try:
            ap = decode_token(acc, token_type="access")
            if (aj := ap.get("jti")) and (ax := ap.get("exp")):
                await blacklist_jti(aj, datetime.fromtimestamp(ax, tz=timezone.utc))
        except Exception:
            pass

    # 3) 쿠키 삭제
    clear_auth_cookies(response)
    return MessageResponse(message="logged out")
