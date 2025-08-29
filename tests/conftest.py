# tests/conftest.py
import os, sys
os.environ["USE_FAKE_REPOS"] = "false"          # ← 항상 DB 레포 강제
os.environ["DB_URL"] = "sqlite://:memory:"      # ← 테스트는 인메모리 SQLite
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import httpx
from asgi_lifespan import LifespanManager

from app.main import app
from app.api.core.config import settings


@pytest.fixture(scope="session", autouse=True)
def _test_settings():
    settings.COOKIE_DOMAIN = ""
    settings.COOKIE_SECURE = False
    settings.ACCESS_TOKEN_MINUTES = 5
    settings.REFRESH_TOKEN_DAYS = 1


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
            yield c

@pytest.fixture(autouse=True, scope="function")
def _reset_inmemory_repos_between_tests():
    try:
        from app.api.repositories.memory.user_repo import _reset as user_reset
        user_reset()
    except Exception:
        pass
    try:
        from app.api.repositories.memory.token_blacklist_repo import _reset as bl_reset
        bl_reset()
    except Exception:
        pass