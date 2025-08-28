# app/api/db/database.py
import os
from tortoise import Tortoise
from app.api.core.config import settings


DB_URL = (
    f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

# ✅ Aerich가 사용하는 설정 객체
TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": [
                "app.api.models.user",
                "app.api.models.diary",
                "app.api.models.tag",
                "app.api.models.emotion",
                "app.api.models.notification",
                "app.api.models.revoked_token",
                "app.api.models.token_blacklist",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}


async def init_db() -> None:
    db_url = os.getenv("DB_URL", getattr(settings, "DB_URL", "sqlite://:memory:"))
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["app.api.models"]},  # 모델 패키지 경로(프로젝트에 맞게)
    )
    # 테스트에서 마이그레이션 대신 스키마 직접 생성
    await Tortoise.generate_schemas(safe=True)

async def close_db() -> None:
    await Tortoise.close_connections()

# ✅ FastAPI 앱 구동 시 호출
async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    # await Tortoise.generate_schemas()


# ✅ 종료 시 연결 해제
async def close_db():
    await Tortoise.close_connections()
