from app.api.core.config import settings

if getattr(settings, "USE_FAKE_REPOS", False):
    from .memory.token_blacklist_repo import *  # noqa: F401,F403
else:
    from .db.token_blacklist_repo import *  # noqa: F401,F403
