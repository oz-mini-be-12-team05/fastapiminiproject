# app/api/db/database.py

from tortoise import Tortoise
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

DB_URL = f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}" \
         f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

# ✅ Aerich가 사용하는 설정 객체
TORTOISE_ORM = {
    "connections": {
        "default": DB_URL,
    },
    "apps": {
        "models": {
            "models": ["app.api.models", "aerich.models"],  # 모델 경로 등록 (aerich.models는 꼭 포함!)
            "default_connection": "default",
        }
    }
}


# ✅ FastAPI 앱 구동 시 호출
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


# ✅ 종료 시 연결 해제
async def close_db():
    await Tortoise.close_connections()
