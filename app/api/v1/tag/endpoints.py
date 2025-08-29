# app/api/v1/tag/endpoints.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ConfigDict

from app.api.core.security import get_current_user
from app.api.repositories.tag_repo import (
    list_tags as repo_list,
    create_tag as repo_create,
    delete_tag as repo_delete,
)

router = APIRouter(prefix="/tags", tags=["tag"])


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    model_config = ConfigDict(json_schema_extra={"example": {"name": "work"}})


class TagOut(BaseModel):
    id: int
    name: str


@router.get("/ping")
async def ping():
    return {"ok": True}


@router.get("", response_model=list[TagOut])
async def list_tags(user=Depends(get_current_user)):
    tags = await repo_list(user)  # ✅ user 객체 그대로 전달
    return [TagOut(id=t.id, name=t.name) for t in tags]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TagOut)
async def create_tag(payload: TagCreate, user=Depends(get_current_user)):
    try:
        t = await repo_create(user, payload.name)  # ✅ 비동기 repo 호출
        return TagOut(id=t.id, name=t.name)
    except ValueError:
        # tag_repo.create_tag에서 중복 시 ValueError 던지는 계약
        raise HTTPException(status_code=409, detail="Tag already exists")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, user=Depends(get_current_user)):
    ok = await repo_delete(user, tag_id)  # ✅ 비동기 & user 객체
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")
    return None
