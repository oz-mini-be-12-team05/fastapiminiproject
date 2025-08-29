# app/api/repositories/user_repo.py
from __future__ import annotations

from app.api.core.config import settings

USE_FAKE = bool(getattr(settings, "USE_FAKE_REPOS", False))

if USE_FAKE:
    # 테스트/로컬: 인메모리 리포지토리 사용
    from .memory.user_repo import *  # noqa: F401,F403
else:
    # 런타임/실서버: DB 리포지토리 사용
    from .db.user_repo import *  # noqa: F401,F403
