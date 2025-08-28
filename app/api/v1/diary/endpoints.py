# app/api/v1/diary/endpoints.py
from __future__ import annotations

from typing import Optional
from datetime import date
from fastapi import (
    APIRouter, Depends, HTTPException, Query, Response, status
)

from app.api.core.security import get_current_user
from app.api.schemas import DiaryCreate, DiaryUpdate, DiaryOut
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


# 작성 (mission_2)
@router.post("", status_code=status.HTTP_201_CREATED, response_model=DiaryOut)
async def create_diary_api(payload: DiaryCreate, user=Depends(get_current_user)):
    diary = await create_diary(user, payload.model_dump())
    return diary


# 조회 + 검색/정렬/페이징 (mission_3, mission_6)
@router.get("", response_model=list[DiaryOut])
async def list_diaries_api(
    page: int = 1,
    page_size: int = 20,
    q: Optional[str] = Query(None, description="제목/내용 검색어"),
    date_from: Optional[date] = Query(None, description="시작 날짜"),
    date_to: Optional[date] = Query(None, description="끝 날짜"),
    order: str = Query("desc", pattern="^(asc|desc)$", description="정렬: asc|desc"),
    user=Depends(get_current_user),
):
    diaries = await list_diaries(
        user=user,
        page=page,
        page_size=page_size,
        q=q,
        date_from=date_from,
        date_to=date_to,
        order=order,
    )
    return diaries


# 단건 조회 (mission_3)
@router.get("/{diary_id}", response_model=DiaryOut)
async def get_diary_api(diary_id: int, user=Depends(get_current_user)):
    diary = await get_diary_by_id_for_user(user, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")
    return diary


# 수정 (mission_4)
@router.patch("/{diary_id}", response_model=DiaryOut)
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
    return diary


# 삭제 (mission_5)
@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary_api(diary_id: int, user=Depends(get_current_user)):
    diary = await get_diary_by_id_for_user(user, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    await delete_diary(diary)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
