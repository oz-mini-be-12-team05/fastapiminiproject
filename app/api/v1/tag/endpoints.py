# app/api/v1/tag/endpoints.py
from __future__ import annotations  # (선택) list[...] 전방참조 안전장치
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.api.core.security import get_current_user

router = APIRouter(prefix="/tags", tags=["tag"])

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)

class TagOut(BaseModel):
    id: int
    name: str

@router.get("/ping")
async def ping():
    return {"ok": True}

@router.get("", response_model=list[TagOut])
async def list_tags(user=Depends(get_current_user)):
    # TODO: 나중에 DB repo 연동
    return []

@router.post("", status_code=status.HTTP_201_CREATED, response_model=TagOut)
async def create_tag(payload: TagCreate, user=Depends(get_current_user)):
    # TODO: 나중에 DB repo 연동
    return TagOut(id=1, name=payload.name)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, user=Depends(get_current_user)):
    # TODO: 나중에 DB repo 연동
    return
