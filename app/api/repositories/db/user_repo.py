# app/api/repositories/user_repo.py
from app.api.models.user import User

# app/api/repositories/user_repo.py
from app.api.core.config import settings
from app.api.db.model import User  # Tortoise ORM 모델 가정

# ...다른 함수들 옆에 추가
async def get_user_by_id(user_id: int):
    # 없으면 None
    return await User.get_or_none(id=user_id)

async def delete_user(user_id: int) -> bool:
    user = await User.get_or_none(id=user_id)
    if not user:
        return False
    await user.delete()
    return True

if settings.USE_FAKE_REPOS:
    from .memory.user_repo import *  # noqa
else:
    from .db.user_repo import *  # noqa

async def get_by_email(email: str) -> User | None:
    return await User.get_or_none(email=email)

async def create_user(email: str, name: str, hashed_password: str) -> User:
    return await User.create(email=email, name=name, hashed_password=hashed_password)

async def mark_verified(email: str) -> User | None:
    user = await User.get_or_none(email=email)
    if not user:
        return None
    user.is_verified = True
    await user.save()
    return user

async def update_user(user: User, **fields) -> User:
    # 허용 필드만 업데이트
    allowed = {"name", "nickname", "phone_number", "hashed_password", "is_verified"}
    for k, v in fields.items():
        if k in allowed and v is not None:
            setattr(user, k, v)
    await user.save()
    return user

async def delete_user(user: User) -> None:
    await user.delete()

async def update_user_by_id(user_id: int, **data):
    await User.filter(id=user_id).update(**data)

async def get_user_by_id(user_id: int) -> User | None:
    return await User.get_or_none(id=user_id)

_USERS_BY_EMAIL: dict[str, dict] = {}
_USERS_BY_ID: dict[int, dict] = {}
_SEQ: int = 0

def _reset():
    global _USERS_BY_EMAIL, _USERS_BY_ID, _SEQ
    _USERS_BY_EMAIL.clear()
    _USERS_BY_ID.clear()
    _SEQ = 0