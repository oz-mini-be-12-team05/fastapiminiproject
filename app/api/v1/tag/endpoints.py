from __future__ import annotations
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from app.api.core.security import get_current_user
from app.api.repositories import tag_repo  # ✅ 추가

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
    return [TagOut(id=t.id, name=t.name) for t in tag_repo.list_by_user(user.id)]

@router.post("", status_code=status.HTTP_201_CREATED, response_model=TagOut)
async def create_tag(payload: TagCreate, user=Depends(get_current_user)):
    t = tag_repo.create(user.id, payload.name)
    return TagOut(id=t.id, name=t.name)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, user=Depends(get_current_user)):
    ok = tag_repo.delete(user.id, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")
    return
