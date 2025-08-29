# app/api/repositories/token_blacklist_repo.py
from __future__ import annotations

from app.api.core.config import settings

USE_FAKE = bool(getattr(settings, "USE_FAKE_REPOS", False))

if USE_FAKE:
    from .memory.token_blacklist_repo import *  # noqa: F401,F403
else:
    from .db.token_blacklist_repo import *      # noqa: F401,F403


async def is_jti_blacklisted(jti: str) -> bool:
    return await is_blacklisted(jti)

try:
    __all__  # 있을 수도, 없을 수도
except NameError:
    __all__ = []
__all__ += ["is_jti_blacklisted"]