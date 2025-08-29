from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Union

try:
    from pydantic import SecretStr
except Exception:  # pragma: no cover
    class SecretStr(str):  # 타입 힌트 대체
        def get_secret_value(self) -> str:
            return str(self)

# 타입 힌트용 (없어도 동작)
try:  # pragma: no cover
    from app.api.schemas.user import SignupRequest  # type: ignore
except Exception:  # pragma: no cover
    SignupRequest = Any  # type: ignore

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


def _hash_password(pw: Union[str, SecretStr]) -> str:
    # ✅ 지연 임포트로 순환참조 방지 (security -> user_repo -> security 루프 차단)
    from app.api.core.security import get_password_hash
    return get_password_hash(_to_plain(pw))


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


# ---------- CRUDs (DB 리포와 동일 인터페이스) ----------

async def get_user_by_id(user_id: int) -> Optional[UserObj]:
    return _users_by_id.get(user_id)


async def get_by_email(email: str) -> Optional[UserObj]:
    return _users_by_email.get(email)


async def create_user(
    email: Optional[str] = None,
    name: Optional[str] = None,
    hashed_password: Optional[str] = None,
    *,
    # 편의 파라미터 (선택)
    password: Optional[Union[str, SecretStr]] = None,
    payload: Optional[SignupRequest] = None,
    **extra: Any,
) -> UserObj:
    """
    기본 시그니처는 DB 리포에 맞춤:
      create_user(email, name, hashed_password, **extra) -> User

    - hashed_password가 없으면 password(또는 payload.password)를 해시하여 사용
    - payload가 주어지면 email/name도 payload 기준으로 채움
    """
    e = email
    n = name
    hp = hashed_password
    pw = password

    if payload is not None:
        e = getattr(payload, "email", e)
        n = getattr(payload, "name", n)
        hp = getattr(payload, "hashed_password", hp)
        if hp is None:
            pw = getattr(payload, "password", pw)

    assert e, "email is required"
    if hp is None:
        assert pw is not None, "password is required when hashed_password is not provided"
        hp = _hash_password(pw)

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

    _users_by_id[u.id] = u
    _users_by_email[u.email] = u
    return u


async def update_user_by_id(
    user_id: int,
    data: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Optional[UserObj]:
    """
    - data/kwargs 병합
    - new_password/password -> hashed_password로 자동 변환
    - 허용 필드만 갱신
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
        pass  # 이미 해시 제공
    elif "new_password" in changes:
        pw_plain = changes.pop("new_password")
    elif "password" in changes:
        pw_plain = changes.pop("password")

    if pw_plain is not None:
        changes["hashed_password"] = _hash_password(pw_plain)
    # -------------------------

    allowed = {
        "name", "nickname", "phone_number",
        "is_active", "is_staff", "is_superuser", "is_verified",
        "hashed_password", "last_login",
        # 이메일 변경 허용 시 "email"도 추가하고 아래 재바인딩 로직 보완
    }

    for k, v in list(changes.items()):
        if k in allowed:
            setattr(u, k, v)

    u.updated_at = datetime.now(timezone.utc)

    # 동일 객체 재바인딩
    _users_by_id[u.id] = u
    _users_by_email[u.email] = u
    return u


async def delete_user(user: UserObj) -> None:
    # 인스턴스 기반 삭제 (DB 리포와 인터페이스 맞춤)
    _users_by_id.pop(user.id, None)
    _users_by_email.pop(user.email, None)


async def delete_user_by_id(user_id: int) -> bool:
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


__all__ = [
    "UserObj",
    "get_user_by_id",
    "get_by_email",
    "create_user",
    "update_user_by_id",
    "delete_user",
    "delete_user_by_id",
    "_reset",
]
