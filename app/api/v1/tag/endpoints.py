from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.api.core.security import get_current_user
from app.api.repositories.tag_repo import (
    list_tags as repo_list,
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
    name: Optional[str] = Query(None, description="태그명(정확히 일치)으로 필터"),
    user=Depends(get_current_user),
):
    """태그 전체 조회 + name으로 필터(정확히 일치)"""
    tags = await repo_list(user)
    if name:
        tags = [t for t in tags if t.name == name]
    return [TagOut(id=t.id, name=t.name) for t in tags]


@router.get("/by-name/{name}", response_model=TagOut)
async def get_tag_by_name(name: str, user=Depends(get_current_user)):
    """태그 단건 조회(이름으로, 정확히 일치)"""
    tags = await repo_list(user)
    t = next((x for x in tags if x.name == name), None)
    if not t:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagOut(id=t.id, name=t.name)


@router.get("/{tag_id}", response_model=TagOut)
async def get_tag(tag_id: int, user=Depends(get_current_user)):
    """태그 단건 조회(ID로)"""
    tags = await repo_list(user)
    t = next((x for x in tags if x.id == tag_id), None)
    if not t:
        raise HTTPException(status_code=404, detail="Tag not found")
    return TagOut(id=t.id, name=t.name)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, user=Depends(get_current_user)):
    """태그 삭제(다이어리 생성 시 만들어진 태그를 관리용으로 삭제)"""
    ok = await repo_delete(user, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")
    return None
