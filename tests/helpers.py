# tests/helpers.py
from __future__ import annotations
import httpx

async def _register(
    client: httpx.AsyncClient,
    *,
    email: str = "alice@example.com",
    password: str = "Passw0rd!",
    name: str = "Alice",
):
    payload = {
        "email": email,
        "password": password,
        "password_confirm": password,  # ✔️ 테스트 스키마에 맞춰 추가
        "name": name,
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    assert res.status_code in (200, 201), f"register failed: {res.status_code} {res.text}"
    return res

async def _login_bearer(
    client: httpx.AsyncClient,
    *,
    email: str = "alice@example.com",
    password: str = "Passw0rd!",
):
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, f"login bearer failed: {res.status_code} {res.text}"
    data = res.json()
    headers = {"Authorization": f"Bearer {data['access_token']}"}
    return data["access_token"], data["refresh_token"], headers

async def _login_cookie(
    client: httpx.AsyncClient,
    *,
    email: str = "alice@example.com",
    password: str = "Passw0rd!",
):
    res = await client.post(
        "/api/v1/auth/login",
        params={"as_cookie": "true"},
        json={"email": email, "password": password},
    )
    assert res.status_code == 200, f"login cookie failed: {res.status_code} {res.text}"
    return res
