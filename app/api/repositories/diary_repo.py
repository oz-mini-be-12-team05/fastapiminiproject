# app/api/repositories/diary_repo.py
from __future__ import annotations
from typing import Optional, Iterable
from datetime import date
from tortoise.expressions import Q

from app.api.models.diary import Diary  # 모델 경로는 프로젝트 구조에 맞게
from app.api.models.user import User    # 필요시 사용

async def create_diary(user: User, data: dict) -> Diary:
    # 모델 필드명에 맞춰 unpack
    diary = await Diary.create(user=user, **data)
    return diary

async def get_diary_by_id_for_user(user: User, diary_id: int) -> Optional[Diary]:
    return await Diary.get_or_none(id=diary_id, user=user)

async def list_diaries(
    user: User,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    order: str = "desc",  # 'asc' 또는 'desc'
) -> Iterable[Diary]:
    qs = Diary.filter(user=user)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    order_by = "-date" if order == "desc" else "date"
    qs = qs.order_by(order_by, "-id")

    offset = max(page - 1, 0) * page_size
    return await qs.offset(offset).limit(page_size)

async def update_diary(diary: Diary, data: dict) -> Diary:
    for k, v in data.items():
        setattr(diary, k, v)
    await diary.save()
    return diary

async def delete_diary(diary: Diary) -> None:
    await diary.delete()
