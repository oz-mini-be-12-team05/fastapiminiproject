# app/api/repositories/user_repo.py
from app.api.core.config import settings

if settings.USE_FAKE_REPOS:
    from .memory.user_repo import *  # noqa: F401,F403
else:
    from .db.user_repo import *  # noqa: F401,F403


if getattr(settings, "USE_FAKE_REPOS", False):
    # ✅ 테스트/메모리
    from .memory.user_repo import *  # noqa: F401,F403
else:
    # ✅ 실DB 구현 (기존 내용을 옮겨둔 위치로 임포트)
    from .db.user_repo import *  # noqa: F401,F403
