# tests/test_auth.py
import httpx
import pytest

from .helpers import _register, _login_bearer, _login_cookie

@pytest.mark.anyio
async def test_register_and_login_bearer(client):
    await _register(client)
    access, refresh, headers = await _login_bearer(client)
    assert access and refresh
    # Bearer 헤더로 /users/me 접근 가능
    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200

@pytest.mark.anyio
async def test_login_sets_cookies_when_as_cookie_true(client):
    await _register(client, email="cookie@example.com")
    res = await _login_cookie(client, email="cookie@example.com")
    # Set-Cookie 두 개(access_token, refresh_token)가 내려오는지 확인
    set_cookie = res.headers.get("set-cookie", "")
    assert "access_token=" in set_cookie
    assert "refresh_token=" in set_cookie

@pytest.mark.anyio
async def test_refresh_cookie_rotation_and_blacklist(client):
    """
    1) 쿠키 로그인 -> refresh_token 쿠키 획득
    2) /refresh 호출 -> 새 쿠키 발급 + 이전 refresh는 블랙리스트
    3) 이전 refresh로 다시 /refresh 호출 시 401
    """
    await _register(client, email="rot@example.com")
    res_login = await _login_cookie(client, email="rot@example.com")

    # old 쿠키 값을 백업
    old_refresh_cookie = None
    for cookie in client.cookies.jar:
        if cookie.name == "refresh_token":
            old_refresh_cookie = cookie.value
            break
    assert old_refresh_cookie

    # 2) refresh
    res_refresh = await client.post("/api/v1/auth/refresh", params={"as_cookie": "true"})
    assert res_refresh.status_code == 200
    # 쿠키가 새것으로 바뀜
    new_refresh_cookie = None
    for cookie in client.cookies.jar:
        if cookie.name == "refresh_token":
            new_refresh_cookie = cookie.value
            break
    assert new_refresh_cookie and new_refresh_cookie != old_refresh_cookie

    # 3) 이전 refresh로 다시 시도 -> 401
    # httpx CookieJar는 도메인/경로와 결합돼 있어 직접 헤더를 만들어 테스트
    bad_client = httpx.AsyncClient(transport=client._transport, base_url="http://test")
    try:
        bad_client.cookies.set("refresh_token", old_refresh_cookie, domain="", path="/")
        res_bad = await bad_client.post("/api/v1/auth/refresh")
        assert res_bad.status_code == 401
        assert "revoked" in res_bad.text.lower() or "invalid" in res_bad.text.lower()
    finally:
        await bad_client.aclose()

@pytest.mark.anyio
async def test_logout_clears_cookies(client):
    await _register(client, email="bye@example.com")
    await _login_cookie(client, email="bye@example.com")

    res = await client.post("/api/v1/auth/logout")
    assert res.status_code == 200

    # 응답에 Max-Age=0 형태로 쿠키 제거가 내려오는지 검사
    set_cookie = res.headers.get("set-cookie", "")
    assert "access_token=;" in set_cookie or "access_token=" in set_cookie and "Max-Age=0" in set_cookie
    assert "refresh_token=;" in set_cookie or "refresh_token=" in set_cookie and "Max-Age=0" in set_cookie
