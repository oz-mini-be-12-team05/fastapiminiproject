# app/api/repositories/diary_repo.py
from __future__ import annotations
from typing import Optional, Iterable, List, Literal
from datetime import date
from tortoise.expressions import Q

from app.api.models.diary import Diary
from app.api.models.user import User


ALLOWED_UPDATE_FIELDS = {
    "title", "content", "mood", "date", "is_private", "tags",
}


async def create_diary(user: User, data: dict) -> Diary:
    """
    - date가 없으면 today()로 보정(최신순 정렬 안정성)
    - tags 저장 방식(DB 설계)에 따라 분기: JSON/Text vs M2M
    """
    payload = dict(data)
    if not payload.get("date"):
        payload["date"] = date.today()

    # ✅ JSON/Text 필드일 때:
    diary = await Diary.create(user=user, **payload)

    # ✅ M2M 태그 모델을 쓰는 경우라면(예시):
    # tags = payload.pop("tags", None)
    # diary = await Diary.create(user=user, **payload)
    # if tags:
    #     # 예: Tag.get_or_create 후 diary.tags.add(tag)
    #     for name in tags:
    #         tag, _ = await Tag.get_or_create(user=user, name=name)
    #         await diary.tags.add(tag)

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
    order: Literal["asc", "desc"] = "desc",
) -> List[Diary]:
    qs = Diary.filter(user=user)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))

    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    # 정렬: date 우선 + 보조 키로 id/created_at까지
    if order == "desc":
        qs = qs.order_by("-date", "-id")  # 필요시 "-created_at"도 추가
    else:
        qs = qs.order_by("date", "id")

    offset = max(page - 1, 0) * page_size
    return await qs.offset(offset).limit(page_size)


async def update_diary(diary: Diary, data: dict) -> Diary:
    """
    - 허용 필드만 업데이트
    - date/정렬 안정성: 필요시 공백/None 보정 가능
    """
    for k, v in data.items():
        if k in ALLOWED_UPDATE_FIELDS:
            setattr(diary, k, v)
    await diary.save()
    return diary


async def delete_diary(diary: Diary) -> None:
    await diary.delete()


# (선택) 페이지네이션 메타가 필요한 경우
async def list_diaries_with_total(
    user: User,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    order: Literal["asc", "desc"] = "desc",
) -> tuple[List[Diary], int]:
    qs = Diary.filter(user=user)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    total = await qs.count()

    if order == "desc":
        qs = qs.order_by("-date", "-id")
    else:
        qs = qs.order_by("date", "id")

    offset = max(page - 1, 0) * page_size
    items = await qs.offset(offset).limit(page_size)
    return items, total
