# app/api/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # JWT/쿠키
    SECRET_KEY: str = "dev-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = 60
    REFRESH_TOKEN_DAYS: int = 7
    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None

    # DB (.env 키와 동일한 이름으로 정의)
    POSTGRES_HOST: str = Field("localhost")
    POSTGRES_PORT: int = Field(5432)
    POSTGRES_USER: str = Field("myuser")
    POSTGRES_PASSWORD: str = Field("1234")
    POSTGRES_DB: str = Field("mydatabase")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 🔽 테스트에서 인메모리 레포를 쓸지 여부
    USE_FAKE_REPOS: bool = Field(default=False, alias="USE_FAKE_REPOS")

    # (선택) 메모리 sqlite를 넘길 때 사용할 수 있게
    DB_URL: str | None = Field(default=None, alias="DB_URL")


    # pydantic-settings v2 설정
    model_config = SettingsConfigDict(
        env_file=".env",     # 프로젝트 루트의 .env 사용
        env_prefix="",       # 접두사 없음
        case_sensitive=False,
        extra="ignore",      # 정의 안 된 키가 있어도 무시
    )

settings = Settings()

