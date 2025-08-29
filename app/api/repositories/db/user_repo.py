from __future__ import annotations
from typing import Optional
from tortoise.exceptions import IntegrityError

from app.api.models.user import User         # (예: app/api/models/user.py 인 경우)

async def get_user_by_id(user_id: int) -> Optional[User]:
    return await User.get_or_none(id=user_id)

async def get_by_email(email: str) -> Optional[User]:
    return await User.get_or_none(email=email)

async def create_user(email: str, name: str, hashed_password: str) -> User:
    try:
        return await User.create(email=email, name=name, hashed_password=hashed_password)
    except IntegrityError:
        # 레포에선 도메인 예외로 변환
        raise ValueError("email already exists")

async def mark_verified(email: str) -> Optional[User]:
    user = await User.get_or_none(email=email)
    if not user:
        return None
    user.is_verified = True
    await user.save()
    return user

async def update_user(user: User, **fields) -> User:
    allowed = {"name", "nickname", "phone_number", "hashed_password", "is_verified"}
    for k, v in fields.items():
        if k in allowed and v is not None:
            setattr(user, k, v)
    await user.save()
    return user

async def update_user_by_id(user_id: int, **fields) -> Optional[User]:
    updated = await User.filter(id=user_id).update(**fields)
    if not updated:
        return None
    return await User.get(id=user_id)

async def delete_user(user: User) -> None:
    await user.delete()

async def delete_user_by_id(user_id: int) -> bool:
    user = await User.get_or_none(id=user_id)
    if not user:
        return False
    await user.delete()
    return True

__all__ = [
    "get_user_by_id",
    "get_by_email",
    "create_user",
    "mark_verified",
    "update_user",
    "update_user_by_id",
    "delete_user",
    "delete_user_by_id",
]
