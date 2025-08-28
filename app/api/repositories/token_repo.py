from datetime import datetime, timezone
from app.api.models.revoked_token import RevokedToken

async def revoke_refresh(jti: str, user_id: int | None, exp_ts: int) -> None:
    # exp_ts는 JWT의 exp(초 단위 epoch)
    expires_at = datetime.fromtimestamp(exp_ts, tz=timezone.utc)
    await RevokedToken.get_or_create(jti=jti, defaults={"user_id": user_id, "expires_at": expires_at})

async def is_refresh_revoked(jti: str) -> bool:
    return await RevokedToken.exists(jti=jti)

# 선택: 청소(만료 지난 블랙리스트 제거)
async def purge_revoked_expired(now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    deleted = await RevokedToken.filter(expires_at__lt=now).delete()
    return deleted

