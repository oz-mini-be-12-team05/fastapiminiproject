# app/api/repositories/memory/user_repo.py
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

from pydantic import SecretStr

# 해시만 쓰도록 import (순환참조 방지: security.py가 user_repo를 import 하지 않게 유지)
# from app.api.core.security import hash_password
from app.api.core.security import get_password_hash
try:
    # 타입 힌트용 (테스트에선 없어도 동작)
    from app.api.schemas.user import SignupRequest  # type: ignore
except Exception:  # pragma: no cover
    SignupRequest = Any  # 타입 힌트만 필요할 때 대체


# ---------- In-Memory Storage ----------
_users_by_email: Dict[str, "UserObj"] = {}
_users_by_id: Dict[int, "UserObj"] = {}
_seq = 0


def _new_id() -> int:
    global _seq
    _seq += 1
    return _seq


def _to_plain(pw: Union[str, SecretStr]) -> str:
    return pw.get_secret_value() if isinstance(pw, SecretStr) else str(pw)


@dataclass
class UserObj:
    id: int
    email: str
    name: str = ""
    hashed_password: str = ""
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    is_verified: bool = False
    nickname: Optional[str] = None
    phone_number: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # FastAPI/Pydantic 직렬화 보조
    def dict(self) -> Dict[str, Any]:
        return asdict(self)


# ---------- CRUDs used by endpoints/security ----------

async def create_user(
    payload: Optional[SignupRequest] = None,
    *,
    email: Optional[str] = None,
    password: Optional[Union[str, SecretStr]] = None,
    hashed_password: Optional[str] = None,
    name: Optional[str] = None,
    **extra: Any,
) -> UserObj:
    """
    - payload가 있으면 payload 우선으로 값 사용
    - hashed_password가 없으면 password를 해시해서 저장
    """
    e = email
    n = name
    hp = hashed_password
    pw = password

    if payload is not None:
        e = getattr(payload, "email", e)
        n = getattr(payload, "name", n)
        # 스키마에 hashed_password가 없을 수도 있으므로 getattr로 안전 접근
        hp = getattr(payload, "hashed_password", hp)
        if hp is None:
            pw = getattr(payload, "password", pw)

    assert e, "email is required"
    if hp is None:
        assert pw is not None, (
            "password is required when hashed_password is not provided"
        )
        hp = get_password_hash(_to_plain(pw))

    # 이메일 중복
    if e in _users_by_email:
        raise ValueError("email already exists")

    u = UserObj(
        id=_new_id(),
        email=e,
        name=n or "",
        hashed_password=hp,
        is_active=True,
        is_staff=False,
        is_superuser=False,
        is_verified=False,
    )

    # 같은 객체를 두 맵에 바인딩(사본 금지)
    _users_by_id[u.id] = u
    _users_by_email[u.email] = u
    return u


async def get_by_email(email: str) -> Optional[UserObj]:
    return _users_by_email.get(email)


async def get_user_by_id(user_id: int) -> Optional[UserObj]:
    return _users_by_id.get(user_id)


async def update_user_by_id(
    user_id: int,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Optional[UserObj]:
    """
    - data/kwargs 병합
    - new_password/password -> hashed_password로 자동 변환
    - 허용 필드만 갱신
    - 두 맵 모두 동일 객체로 재바인딩(안전)
    """
    u = _users_by_id.get(user_id)
    if not u:
        return None

    changes: Dict[str, Any] = {}
    if data:
        changes.update(data)
    if kwargs:
        changes.update(kwargs)

    # ---- 비밀번호 키 처리 ----
    pw_plain = None
    if "hashed_password" in changes:
        # 이미 해시로 제공되면 그대로
        pass
    elif "new_password" in changes:
        pw_plain = changes.pop("new_password")
    elif "password" in changes:
        pw_plain = changes.pop("password")

    if pw_plain is not None:
        changes["hashed_password"] = get_password_hash(_to_plain(pw_plain))
        # -------------------------

    allowed = {
        "name", "nickname", "phone_number",
        "is_active", "is_staff", "is_superuser", "is_verified",
        "hashed_password", "last_login",
        # 이메일 변경 허용 시 "email"도 추가하고 하단 재바인딩 로직 보완
    }

    for k, v in list(changes.items()):
        if k in allowed:
            setattr(u, k, v)

    u.updated_at = datetime.now(timezone.utc)

    # 안전하게 두 맵 모두 동일 객체로 재바인딩
    _users_by_id[u.id] = u
    _users_by_email[u.email] = u
    return u


async def delete_user(user_id: int) -> bool:
    u = _users_by_id.pop(user_id, None)
    if not u:
        return False
    _users_by_email.pop(u.email, None)
    return True


# 테스트에서 리셋용
def _reset() -> None:
    _users_by_email.clear()
    _users_by_id.clear()
    global _seq
    _seq = 0
