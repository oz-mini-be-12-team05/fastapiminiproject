# app/api/repositories/diary_repo.py
from __future__ import annotations
from typing import Optional, List, Literal
from datetime import date
from tortoise.expressions import Q

from app.api.models.diary import Diary
from app.api.models.tag import Tag
from app.api.models.user import User


ALLOWED_UPDATE_FIELDS = {
    "title", "content", "mood", "date", "is_private", "ai_summary",
}


def _norm_tags(names: Optional[List[str]]) -> List[str]:
    """문자열 리스트 정규화: trim, 빈값 제거, 중복 제거(순서 보존)"""
    if not names:
        return []
    seen, out = set(), []
    for n in names:
        s = str(n).strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


async def create_diary(user: User, data: dict) -> Diary:
    """
    - date 기본값 보정
    - tags(M2M) 연결: 문자열 리스트를 Tag 엔티티로 정규화 후 add
    """
    payload = dict(data)
    tag_names = _norm_tags(payload.pop("tags", None))
    if not payload.get("date"):
        payload["date"] = date.today()

    diary = await Diary.create(user=user, **payload)

    for name in tag_names:
        t, _ = await Tag.get_or_create(user=user, name=name)
        await diary.tags.add(t)

    return diary


async def get_diary_by_id_for_user(user: User, diary_id: int) -> Optional[Diary]:
    # 태그도 함께 보고 싶으면 prefetch:
    return await (
        Diary.filter(id=diary_id, user=user)
        .prefetch_related("tags")
        .first()
    )


async def list_diaries(
    user: User,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    order: Literal["asc", "desc"] = "desc",
    tags_any: Optional[List[str]] = None,   # 태그 ANY
    tags_all: Optional[List[str]] = None,   # 태그 ALL
) -> List[Diary]:
    qs = Diary.filter(user=user)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    any_norm = _norm_tags(tags_any)
    all_norm = _norm_tags(tags_all)

    if any_norm:
        qs = qs.filter(tags__name__in=any_norm).distinct()
    if all_norm:
        for t in all_norm:
            qs = qs.filter(tags__name=t)
        qs = qs.distinct()


    if order == "desc":
        qs = qs.order_by("-date", "-id")
    else:
        qs = qs.order_by("date", "id")

    qs = qs.prefetch_related("tags")

    offset = max(page - 1, 0) * page_size
    return await qs.offset(offset).limit(page_size)


async def update_diary(diary: Diary, data: dict) -> Diary:
    """
    - 허용 필드만 업데이트
    - tags가 들어오면 전체 교체(clear → add)
    """
    changes = dict(data)
    tag_names = _norm_tags(changes.pop("tags", None))

    for k, v in changes.items():
        if k in ALLOWED_UPDATE_FIELDS:
            setattr(diary, k, v)
    await diary.save()

    if tag_names is not None:
        await diary.tags.clear()
        for name in tag_names:
            t, _ = await Tag.get_or_create(user=diary.user, name=name)
            await diary.tags.add(t)

    return diary


async def delete_diary(diary: Diary) -> None:
    await diary.delete()


# (선택) total 포함 버전
async def list_diaries_with_total(
    user: User,
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    order: Literal["asc", "desc"] = "desc",
    tags_any: Optional[List[str]] = None,
    tags_all: Optional[List[str]] = None,
) -> tuple[List[Diary], int]:
    qs = Diary.filter(user=user)

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q))  # ← 오타 fix
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    any_norm = _norm_tags(tags_any)
    all_norm = _norm_tags(tags_all)

    if any_norm:
        qs = qs.filter(tags__name__in=any_norm).distinct()
    if all_norm:
        for t in all_norm:
            qs = qs.filter(tags__name=t)
        qs = qs.distinct()

    total = await qs.count()

    qs = qs.prefetch_related("tags")
    qs = qs.order_by("-date", "-id") if order == "desc" else qs.order_by("date", "id")

    offset = max(page - 1, 0) * page_size
    items = await qs.offset(offset).limit(page_size)
    return items, total
