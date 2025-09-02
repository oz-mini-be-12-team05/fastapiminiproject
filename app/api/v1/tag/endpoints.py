# app/api/v1/tag/endpoints.py
from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field, ConfigDict

from app.api.core.security import get_current_user
from app.api.repositories.tag_repo import (
    list_tags as repo_list,
    # create_tag 제거
    delete_tag as repo_delete,
)

router = APIRouter(prefix="/tags", tags=["tag"])


class TagOut(BaseModel):
    id: int
    name: str


@router.get("/ping")
async def ping():
    return {"ok": True}


@router.get("", response_model=list[TagOut])
async def list_tags(
    name: Optional[str] = Query(None, description="이름으로 필터 조회(정확히 일치)"),
    user=Depends(get_current_user),
):
    """태그 목록 조회. name이 주어지면 해당 이름으로 필터."""
    tags = await repo_list(user)
    if name:
        tags = [t for t in tags if t.name == name]  # 필요시 lower()로 케이스 무시 가능
    return [TagOut(id=t.id, name=t.name) for t in tags]


@router.get("/by-name/{name}", response_model=TagOut)
async def get_tag_by_name(name: str, user=Depends(get_current_user)):
    """태그 단건 조회(이름). 정확히 일치하는 첫 태그 반환."""
    tags = await repo_list(user)
    t = next((x for x in tags if x.name == name), None)
    if not t:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagOut(id=t.id, name=t.name)


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: int, user=Depends(get_current_user)):
    """태그 단건 조회(ID)."""
    tags = await repo_list(user)
    t = next((x for x in tags if x.id == tag_id), None)
    if not t:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagOut(id=t.id, name=t.name)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, user=Depends(get_current_user)):
    """태그 삭제(ID). 다이어리에 사용중인 경우 레포/DB 제약에 따라 에러날 수 있음."""
    ok = await repo_delete(user, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")
    return None
