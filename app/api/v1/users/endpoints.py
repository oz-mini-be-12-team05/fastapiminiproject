# app/api/v1/users/endpoints.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.api.core.security import (
    decode_token,
    get_current_user,
    verify_password,
    clear_auth_cookies,
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
    return user


@router.patch("/me", response_model=UserOut)
async def update_me(payload: UpdateMeRequest, user=Depends(get_current_user)):
    """
    - 현재 비밀번호 검증은 여기서 수행
    - 실제 비밀번호 해시는 리포지토리(update_user_by_id)가 담당
    """
    data = payload.model_dump(exclude_unset=True)

    # 비밀번호 변경 요청?
    if "new_password" in data:
        if "current_password" not in data:
            raise HTTPException(
                status_code=422,
                detail="current_password is required to change password",
            )

        # 현재 비번 검증
        if not verify_password(
            data["current_password"].get_secret_value(),
            user.hashed_password,
        ):
            raise HTTPException(status_code=400, detail="current password is incorrect")

        # 리포지토리에서 해시하도록 'new_password'만 전달
        # (SecretStr 그대로 넘겨도 repo가 평문으로 변환해 해시함)
        data.pop("current_password", None)

    # 전달 허용 키
    allowed = {"name", "nickname", "phone_number", "new_password", "password"}
    filtered = {k: v for k, v in data.items() if k in allowed}

    if filtered:
        await update_user_by_id(user.id, **filtered)

    return await get_user_by_id(user.id)


@router.delete("/me", response_model=MessageResponse)
async def delete_me(request: Request, response: Response, user=Depends(get_current_user)):
    # refresh 토큰 jti 블랙리스트
    if (rt := request.cookies.get("refresh_token")):
        try:
            p = decode_token(rt, token_type="refresh")
            if (jti := p.get("jti")) and (exp := p.get("exp")):
                await blacklist_jti(jti, datetime.fromtimestamp(exp, tz=timezone.utc))
        except Exception:
            pass

    # access 토큰도 블랙리스트
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        acc = auth.split(" ", 1)[1]
        try:
            ap = decode_token(acc, token_type="access")
            if (aj := ap.get("jti")) and (ax := ap.get("exp")):
                await blacklist_jti(aj, datetime.fromtimestamp(ax, tz=timezone.utc))
        except Exception:
            pass

    # 리포지토리는 user_id를 받습니다.
    await delete_user(user.id)
    clear_auth_cookies(response)
    return MessageResponse(message="Deleted successfully")
