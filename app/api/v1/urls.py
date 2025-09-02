# app/api/v1/urls.py
from fastapi import APIRouter

from .auth.urls import router as auth_router
from .ai.urls import router as ai_router
from .diary.urls import router as diary_router
from .users.urls import router as users_router
from app.api.v1.tag.endpoints import router as tag_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(ai_router)
api_router.include_router(diary_router)
api_router.include_router(tag_router)
api_router.include_router(users_router)




__all__ = ["api_router"]
