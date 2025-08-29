# app/api/v1/users/endpoints.py
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import SecretStr

from app.api.core.security import (
    decode_token,
    get_current_user,
    verify_password,
    clear_auth_cookies,
    get_password_hash,
)
from app.api.repositories.token_blacklist_repo import blacklist_jti
from app.api.repositories.user_repo import (
    get_user_by_id,
    update_user_by_id,
    delete_user,
)
from app.api.schemas import MessageResponse, UpdateMeRequest, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(user=Depends(get_current_user)):
    # schemas.UserOut 에 from_attributes=True 설정이 있으므로 그대로 반환 OK
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(payload: UpdateMeRequest, user=Depends(get_current_user)):
    data = payload.model_dump(exclude_unset=True)

    # ---- 비밀번호 변경 처리 ----
    cur = data.pop("current_password", None)
    new = data.pop("new_password", None)
    if new is not None:
        cur_plain = cur.get_secret_value() if isinstance(cur, SecretStr) else cur
        if not cur_plain or not verify_password(cur_plain, user.hashed_password):
            raise HTTPException(status_code=400, detail="Current password mismatch")

        new_plain = new.get_secret_value() if isinstance(new, SecretStr) else new
        data["hashed_password"] = get_password_hash(new_plain)
    # ---------------------------

    # 허용 필드만 업데이터에 전달
    allowed = {"name", "nickname", "phone_number", "hashed_password"}
    filtered = {k: v for k, v in data.items() if k in allowed}

    if filtered:
        await update_user_by_id(user.id, **filtered)
        user = await get_user_by_id(user.id)

    return UserOut.model_validate(user)


@router.delete("/me", response_model=MessageResponse)
async def delete_me(request: Request, response: Response, user=Depends(get_current_user)):
    # refresh 토큰 블랙리스트
    if (rt := request.cookies.get("refresh_token")):
        try:
            p = decode_token(rt, token_type="refresh")
            if (jti := p.get("jti")) and (exp := p.get("exp")):
                await blacklist_jti(jti, datetime.fromtimestamp(exp, tz=timezone.utc))
        except Exception:
            pass

    # access 토큰 블랙리스트
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        acc = auth.split(" ", 1)[1]
        try:
            ap = decode_token(acc, token_type="access")
            if (aj := ap.get("jti")) and (ax := ap.get("exp")):
                await blacklist_jti(aj, datetime.fromtimestamp(ax, tz=timezone.utc))
        except Exception:
            pass

    await delete_user(user.id)
    clear_auth_cookies(response)
    return MessageResponse(message="Deleted successfully")
