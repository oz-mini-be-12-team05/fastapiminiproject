# app/api/repositories/db/token_blacklist_repo.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

# 🔧 실제 프로젝트 구조에 맞게 모델 경로를 하나만 선택해서 사용하세요.
# 예: from app.api.models.token_blacklist import TokenBlacklist
# 또는: from app.db.models.token_blacklist import TokenBlacklist
from app.api.models.token_blacklist import TokenBlacklist  # 예시

async def blacklist_jti(jti: str, expires_at: datetime) -> None:
    # 이미 존재하면 업데이트, 없으면 생성 (DB 종속 로직)
    obj = await TokenBlacklist.get_or_none(jti=jti)
    if obj:
        obj.expires_at = expires_at
        await obj.save()
    else:
        await TokenBlacklist.create(jti=jti, expires_at=expires_at)

async def is_blacklisted(jti: str) -> bool:
    obj = await TokenBlacklist.get_or_none(jti=jti)
    if not obj:
        return False
    # 만료된 항목은 블랙리스트에서 의미 없음
    return obj.expires_at > datetime.now(timezone.utc)

async def purge_expired(now: Optional[datetime] = None) -> int:
    """만료된 항목 일괄 삭제 후 삭제 개수 반환"""
    now = now or datetime.now(timezone.utc)
    # Tortoise 예시:
    deleted = await TokenBlacklist.filter(expires_at__lte=now).delete()
    return deleted

__all__ = ["blacklist_jti", "is_blacklisted", "purge_expired"]
