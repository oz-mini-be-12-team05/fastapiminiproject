# app/api/db/database.py
from __future__ import annotations

import os
from tortoise import Tortoise
from app.api.core.config import settings


def _resolve_db_url() -> str:
    """
    우선순위
    1) 환경변수 DB_URL
    2) settings.DB_URL
    3) Postgres 구성요소로 DSN 조합
    4) 기본: sqlite 메모리
    """
    env_url = os.getenv("DB_URL")
    if env_url:
        return env_url

    if getattr(settings, "DB_URL", None):
        return settings.DB_URL

    required = (
        getattr(settings, "POSTGRES_USER", None),
        getattr(settings, "POSTGRES_PASSWORD", None),
        getattr(settings, "POSTGRES_HOST", None),
        getattr(settings, "POSTGRES_PORT", None),
        getattr(settings, "POSTGRES_DB", None),
    )
    if all(required):
        return (
            f"postgres://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
            f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

    return "sqlite://:memory:"


def build_tortoise_config(db_url: str | None = None) -> dict:
    """
    Aerich가 그대로 읽을 수 있는 설정 객체 생성.
    """
    db_url = db_url or _resolve_db_url()
    return {
        "connections": {"default": db_url},
        "apps": {
            "models": {
                "models": [
                    # ← 개별 모델 모듈을 명시하면 re-export 없이도 안전합니다.
                    "app.api.models.user",
                    "app.api.models.tag",
                    "app.api.models.emotion",
                    "app.api.models.notification",
                    "app.api.models.revoked_token",
                    "app.api.models.token_blacklist",
                    "app.api.models.diary",
                    "aerich.models",
                ],
                "default_connection": "default",
            }
        },
    }


# ✅ Aerich가 이 변수를 import 해서 씁니다.
TORTOISE_ORM = build_tortoise_config()


async def init_db() -> None:
    """
    - 운영(Postgres)은 Aerich 마이그레이션 사용 → generate_schemas() 호출 X
    - 테스트/로컬(SQLite)은 자동 스키마 생성 허용
    """
    db_url = _resolve_db_url()
    await Tortoise.init(config=build_tortoise_config(db_url))

    if db_url.startswith("sqlite://"):
        await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    await Tortoise.close_connections()
