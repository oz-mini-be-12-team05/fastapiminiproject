# app/api/repositories/memory/token_blacklist_repo.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict

_blacklist: Dict[str, datetime] = {}

async def add_to_blacklist(jti: str, expires_at: datetime) -> None:
    _blacklist[jti] = expires_at

# (호환용) 예전에 쓰던 이름이 있으면 이렇게 별칭으로 유지
blacklist_jti = add_to_blacklist

async def is_jti_blacklisted(jti: str) -> bool:
    exp = _blacklist.get(jti)
    if exp is None:
        return False
    # 만료된 항목은 즉시 청소
    if exp <= datetime.now(timezone.utc):
        _blacklist.pop(jti, None)
        return False
    return True

async def purge_expired(now: datetime | None = None) -> int:
    """만료된 블랙리스트 항목 삭제하고 삭제 개수 반환."""
    if now is None:
        now = datetime.now(timezone.utc)
    # 순회 중 변경 방지: list()로 복사
    expired = [j for j, exp in list(_blacklist.items()) if exp <= now]
    for j in expired:
        _blacklist.pop(j, None)
    return len(expired)

def _reset() -> None:
    _blacklist.clear()
