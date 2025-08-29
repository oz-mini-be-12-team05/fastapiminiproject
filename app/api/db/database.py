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
    Aerich와 동일하게 사용할 수 있는 설정 객체 생성.
    models 패키지가 __init__.py에서 모든 모델을 re-export 해야 함.
    (만약 re-export가 없다면 아래 리스트를 각 모델 경로로 바꿔도 됩니다.)
    """
    db_url = db_url or _resolve_db_url()
    return {
        "connections": {"default": db_url},
        "apps": {
            "models": {
                "models": [
                    "app.api.models",   # ← 패키지 경로 (User, Diary, Tag 등 re-export 필요)
                    "aerich.models",
                ],
                "default_connection": "default",
            }
        },
    }


async def init_db() -> None:
    """
    - 운영(예: Postgres)에서는 Aerich 마이그레이션을 사용 → 스키마 자동생성 X
    - 테스트/로컬(SQLite)에서는 스키마 자동생성으로 간단히 구동
    """
    db_url = _resolve_db_url()
    await Tortoise.init(config=build_tortoise_config(db_url))

    # 테스트 시(DB_URL=sqlite://...) 자동 스키마 생성
    if db_url.startswith("sqlite://"):
        await Tortoise.generate_schemas(safe=True)


async def close_db() -> None:
    await Tortoise.close_connections()
