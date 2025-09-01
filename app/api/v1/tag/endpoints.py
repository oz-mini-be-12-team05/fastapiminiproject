from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status, Response
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
    tags = await repo_list(user)
    return [TagOut(id=t.id, name=t.name) for t in tags]


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TagOut)
async def create_tag(payload: TagCreate, user=Depends(get_current_user)):
    try:
        t = await repo_create(user, payload.name)
        return TagOut(id=t.id, name=t.name)
    except ValueError:
        raise HTTPException(status_code=409, detail="Tag already exists")


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: int, user=Depends(get_current_user)):
    # 1️⃣ 태그에 연결된 일기 확인
    diaries_with_tag = await db.fetch_all(
        "SELECT * FROM diaries WHERE tags @> :tag",
        values={"tag": [tag_id]}
    )
    if diaries_with_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete tag because it is associated with diaries"
        )

    # 2️⃣ 실제 삭제
    ok = await repo_delete(user, tag_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tag not found")

    # 3️⃣ 204 No Content 반환
    return Response(status_code=status.HTTP_204_NO_CONTENT)