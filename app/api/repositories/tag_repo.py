# 지금은 메모리 repo에 위임. DB repo 만들면 여기서 스위칭.
from __future__ import annotations
from .memory import tag_repo as mem
# app/api/repositories/tag_repo.py
from typing import List, Optional
from tortoise.exceptions import IntegrityError

from app.api.models import Tag, User, Diary

async def list_tags(user: User) -> List[Tag]:
    return await Tag.filter(user=user).order_by("name")

async def create_tag(user: User, name: str) -> Tag:
    try:
        return await Tag.create(user=user, name=name.strip())
    except IntegrityError:
        # 사용자별 중복 이름 방지
        raise ValueError("tag already exists")

async def delete_tag(user: User, tag_id: int) -> bool:
    tag = await Tag.get_or_none(id=tag_id, user=user)
    if not tag:
        return False
    await tag.delete()
    return True

list_by_user = mem.list_by_user
create = mem.create
delete = mem.delete
reset = mem.reset
