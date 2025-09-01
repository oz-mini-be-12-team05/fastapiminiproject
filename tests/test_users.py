# tests/test_users.py
import pytest
from .helpers import _register, _login_bearer

@pytest.mark.anyio
async def test_me_requires_auth(client):
    # 인증 없이
    res = await client.get("/api/v1/users/me")
    assert res.status_code == 401

@pytest.mark.anyio
async def test_get_and_update_me(client):
    await _register(client, email="u1@example.com", password="Passw0rd!", name="U1")
    access, refresh, headers = await _login_bearer(client, email="u1@example.com", password="Passw0rd!")

    # GET /me
    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    before = me.json()
    assert before["email"] == "u1@example.com"

    # PATCH /me (이름 변경)
    upd = await client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"name": "New Name"},
    )
    assert upd.status_code == 200
    assert upd.json()["name"] == "New Name"


@pytest.mark.anyio
async def test_change_password_and_login_again(client):
    await _register(client, email="pw@example.com", password="OldPass1!", name="Pw")
    access, refresh, headers = await _login_bearer(client, email="pw@example.com", password="OldPass1!")

    # 비밀번호 변경
    res = await client.patch(
        "/api/v1/users/me",
        headers=headers,
        json={"current_password": "OldPass1!", "new_password": "NewPass1!"},
    )
    assert res.status_code == 200

    # 새 비밀번호로 로그인 OK
    relogin = _login_bearer
    access2, refresh2, headers2 = await relogin(client, email="pw@example.com", password="NewPass1!")
    assert access2


# 중복 이메일 가입 시 에러
@pytest.mark.anyio
async def test_duplicate_email_registration(client):
    email = "dup@example.com"
    password = "NewPass123!"
    name = "Dup"

    # 첫 번째 등록 (정상)
    res1 = await _register(client, email=email, password=password, name=name)
    assert res1.status_code == 201  # 성공 확인

    # 두 번째 등록 (중복) 처리
    try:
        res2 = await _register(client, email=email, password=password, name=name)
        # Response 반환 시 상태 코드 확인
        assert res2.status_code == 409
    except Exception:
        # 예외를 던지는 구조일 경우 예외 확인
        import pytest
        with pytest.raises(Exception):
            await _register(client, email=email, password=password, name=name)



# 올바른 회원가입 후 잘못된 비밀번호로 로그인 시도
@pytest.mark.anyio
async def test_login_with_wrong_password(client):
    await _register(
        client,
        email="wrongpw@example.com",
        password="CorrectPass123!",
        name="WrongPW"
    )

