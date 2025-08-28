from datetime import datetime, timezone
from app.api.models.token_blacklist import TokenBlacklist

from app.api.core.config import settings

if settings.USE_FAKE_REPOS:
    from .memory.token_blacklist_repo import *  # noqa: F401,F403
else:
    from .db.token_blacklist_repo import *  # noqa: F401,F403

async def blacklist_jti(jti: str, expires_at: datetime) -> None:
    await TokenBlacklist.get_or_create(jti=jti, defaults={"expires_at": expires_at})

async def is_jti_blacklisted(jti: str) -> bool:
    return await TokenBlacklist.filter(jti=jti).exists()


async def purge_expired() -> int:
    now = datetime.now(timezone.utc)
    deleted = await TokenBlacklist.filter(expires_at__lt=now).delete()
    return deleted

_BLACKLIST: dict[str, float] = {}  # jti -> exp_ts (timestamp)

def _reset():
    _BLACKLIST.clear()