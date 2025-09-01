# app/main.py
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router as v1_router
from app.api.db.database import init_db, close_db
from app.api.repositories.token_blacklist_repo import purge_expired

# 1) 환경변수 로드 및 로깅 설정
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2) CORS 설정
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
CORS_CREDENTIALS = os.getenv("CORS_CREDENTIALS", "true").lower() == "true"

# 3) FastAPI 앱 생성
app = FastAPI(
    title="FastAPI Mini Project",
    description="AI + Diary + Auth API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# 4) CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS else ["*"],
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5) 앱 라이프사이클 이벤트
@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    try:
        await purge_expired()
    except Exception as e:
        logger.warning("purge_expired skipped: %s", e)

@app.on_event("shutdown")
async def on_shutdown() -> None:
    try:
        await close_db()
    except Exception as e:
        logger.warning("close_db skipped: %s", e)

# 6) 라우터 등록
app.include_router(v1_router, prefix="/api/v1")

# 7) 헬스체크 엔드포인트
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI + Tortoise + asyncpg!"}

# 8) 로컬 개발용 실행
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )


