# app/api/v1/diary/endpoints.py
from __future__ import annotations

from typing import Optional, Literal, List, Any
from datetime import date, datetime as _dt
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.api.core.security import get_current_user
from app.api.schemas.diary import DiaryCreate, DiaryUpdate  # ⬅ DiaryOut 안 씀
from app.api.repositories.diary_repo import (
    create_diary,
    list_diaries,
    get_diary_by_id_for_user,
    update_diary,
    delete_diary,
)

router = APIRouter(prefix="/diaries", tags=["diary"])


@router.get("/ping")
async def ping():
    return {"ok": True}


def _to_out_dict(d) -> dict[str, Any]:
    """Tortoise Diary -> dict(JSON 직렬화용)"""
    raw_date = getattr(d, "date", None)
    out_date = raw_date.date() if isinstance(raw_date, _dt) else raw_date

    try:
        tag_names = [str(t.name) for t in d.tags]
    except Exception:
        tag_names = []

    return {
        "id": int(d.id),
        "title": str(getattr(d, "title", "")),
        "content": str(getattr(d, "content", "")),
        "mood": getattr(d, "mood", None),
        "date": out_date,
        "is_private": bool(getattr(d, "is_private", True)),
        "tags": tag_names,
        "created_at": getattr(d, "created_at", None),
        "updated_at": getattr(d, "updated_at", None),
    }


# 작성 (mission_2)
@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
async def create_diary_api(
    payload: DiaryCreate,
    response: Response,
    user=Depends(get_current_user),
):
    diary = await create_diary(user, payload.model_dump(exclude_unset=True))
    await diary.fetch_related("tags")
    response.headers["Location"] = f"/api/v1/diaries/{diary.id}"
    return _to_out_dict(diary)


# 조회 + 검색/정렬/페이징 (mission_3, mission_6)
@router.get("", response_model=List[dict])
async def list_diaries_api(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    q: Optional[str] = Query(None, description="제목/내용 검색어"),
    date_from: Optional[date] = Query(None, description="시작 날짜"),
    date_to: Optional[date] = Query(None, description="끝 날짜"),
    order: Literal["asc", "desc"] = Query("desc", description="정렬: asc|desc"),
    tags: Optional[str] = Query(None, description="쉼표구분 태그(ANY)"),
    tags_all: Optional[str] = Query(None, description="쉼표구분 태그(ALL)"),
    user=Depends(get_current_user),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from must be <= date_to")

    any_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    all_list = [t.strip() for t in tags_all.split(",") if t.strip()] if tags_all else None

    diaries = await list_diaries(
        user=user,
        page=page,
        page_size=page_size,
        q=q,
        date_from=date_from,
        date_to=date_to,
        order=order,
        tags_any=any_list,
        tags_all=all_list,
    )

    # 필요시 관계 로드
    for d in diaries:
        try:
            _ = [t.name for t in d.tags]
        except Exception:
            await d.fetch_related("tags")

    return [_to_out_dict(d) for d in diaries]


# 단건 조회 (mission_3)
@router.get("/{diary_id}", response_model=dict)
async def get_diary_api(diary_id: int, user=Depends(get_current_user)):
    diary = await get_diary_by_id_for_user(user, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    await diary.fetch_related("tags")
    return _to_out_dict(diary)


# 수정 (mission_4)
@router.patch("/{diary_id}", response_model=dict)
async def update_diary_api(
    diary_id: int,
    payload: DiaryUpdate,
    user=Depends(get_current_user),
):
    diary = await get_diary_by_id_for_user(user, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    data = payload.model_dump(exclude_unset=True)
    diary = await update_diary(diary, data)
    await diary.fetch_related("tags")
    return _to_out_dict(diary)


# 삭제 (mission_5)
@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary_api(diary_id: int, user=Depends(get_current_user)):
    diary = await get_diary_by_id_for_user(user, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    await delete_diary(diary)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
