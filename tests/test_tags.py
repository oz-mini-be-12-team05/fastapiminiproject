# tests/test_tags.py
import pytest
from .helpers import _register, _login_bearer  # ← 기존 헬퍼 재사용

@pytest.mark.anyio
async def test_tag_crud_and_filter(client):
    # 유저
    await _register(client, email="t@t.com", password="pw123456", name="t")
    access, refresh, headers = await _login_bearer(client, email="t@t.com", password="pw123456")

    # 태그 생성
    r = await client.post("/api/v1/tags", json={"name": "work"}, headers=headers); assert r.status_code in (200, 201)
    r = await client.post("/api/v1/tags", json={"name": "life"}, headers=headers); assert r.status_code in (200, 201)

    # 일기 2개 생성 (각각 다른 태그)
    await client.post("/api/v1/diaries", json={"title": "a", "content": "a", "tags": ["work"]}, headers=headers)
    await client.post("/api/v1/diaries", json={"title": "b", "content": "b", "tags": ["life"]}, headers=headers)

    # 목록 태그 ANY 필터
    r = await client.get("/api/v1/diaries?tags=work", headers=headers)
    assert r.status_code == 200 and all("work" in d["tags"] for d in r.json())

    # 목록 태그 ALL 필터 (해당 없음)
    r = await client.get("/api/v1/diaries?tags_all=work,life", headers=headers)
    assert r.status_code == 200 and r.json() == []

    # 태그 목록
    r = await client.get("/api/v1/tags", headers=headers)
    assert r.status_code == 200 and {t["name"] for t in r.json()} == {"work", "life"}

    # 태그 중복 생성 시 에러
    r = await client.post("/api/v1/tags", json={"name": "work"}, headers=headers)
    assert r.status_code in (400, 409)

    #  태그 목록 조회
    r = await client.get("/api/v1/tags", headers=headers)
    tags = {t["name"] for t in r.json()}
    assert "work" in tags and "life" in tags