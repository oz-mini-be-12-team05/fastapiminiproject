# app/api/repositories/memory/token_blacklist_repo.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

# jti -> expires_at
_store: Dict[str, datetime] = {}

async def blacklist_jti(jti: str, expires_at: datetime) -> None:
    _store[jti] = expires_at

async def is_blacklisted(jti: str) -> bool:
    exp = _store.get(jti)
    if exp is None:
        return False
    # 만료면 의미 없음
    return exp > datetime.now(timezone.utc)

async def purge_expired(now: Optional[datetime] = None) -> int:
    now = now or datetime.now(timezone.utc)
    to_del = [k for k, v in _store.items() if v <= now]
    for k in to_del:
        _store.pop(k, None)
    return len(to_del)

def _reset() -> None:
    _store.clear()

__all__ = ["blacklist_jti", "is_blacklisted", "purge_expired", "_reset"]
