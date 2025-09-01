# app/api/db/database.py
import os
from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()  # .env 파일 로드

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

TORTOISE_CONFIG = {
    "connections": {
        "default": DB_URL
    },
    "apps": {
        "models": {
            "models": ["app.api.models", "aerich.models"],  # aerich.models 포함 필수
            "default_connection": "default",
        }
    }
}

async def init_db():
    """DB 초기화"""
    await Tortoise.init(config=TORTOISE_CONFIG)
    # 개발 환경에서만 자동 스키마 생성 가능
    # await Tortoise.generate_schemas()

async def close_db():
    """DB 연결 종료"""
    await Tortoise.close_connections()