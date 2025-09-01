# app/api/schemas/diary.py
from __future__ import annotations
from typing import Optional, List, Literal
import datetime as dt
from pydantic import BaseModel, Field, ConfigDict, field_validator

class DiaryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=10000)
    mood: Optional[str] = Field(None, max_length=30)
    date: dt.date | None = Field(default=None)   # ← 여기 핵심
    is_private: bool = True
    tags: List[str] = Field(default_factory=list)

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            v = [v]
        if not isinstance(v, (list, tuple)):
            raise ValueError("tags must be a list of strings")
        seen, out = set(), []
        for t in v:
            if t is None:
                continue
            s = str(t).strip()
            if s and s not in seen:
                seen.add(s)
                out.append(s)
        return out

class DiaryCreate(DiaryBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "오늘의 기록",
            "content": "점심에 파스타 먹고 운동 30분.",
            "mood": "happy",
            "date": "2025-08-29",
            "is_private": True,
            "tags": ["food", "exercise"],
        }
    })

class DiaryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    mood: Optional[str] = Field(None, max_length=30)
    date: dt.date | None = Field(default=None)   # ← 동일하게
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags_partial(cls, v):
        if v is None:
            return None
        return DiaryBase._normalize_tags(v)

class DiaryOut(DiaryBase):
    id: int
    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None

    model_config = ConfigDict(from_attributes=True)
