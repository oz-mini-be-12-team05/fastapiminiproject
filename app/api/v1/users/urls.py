# 예: app/api/v1/users/urls.py
from .endpoints import router as _router
router = _router
__all__ = ["router"]
