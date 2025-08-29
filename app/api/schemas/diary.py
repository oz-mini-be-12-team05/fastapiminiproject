from __future__ import annotations
from typing import Optional, List, Literal
from datetime import date, datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator


class DiaryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1, max_length=10000)
    mood: Optional[str] = Field(None, max_length=30)
    date: Optional[date] = None
    is_private: bool = True
    tags: List[str] = Field(default_factory=list)

    # 태그 정규화: 공백제거 → 빈값 제거 → 중복 제거(순서 보존)
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
            if not s:
                continue
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out


class DiaryCreate(DiaryBase):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "오늘의 기록",
            "content": "점심에 파스타 먹음. 운동 30분.",
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
    date: Optional[date] = None
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags_partial(cls, v):
        if v is None:
            return None
        # DiaryBase와 동일한 정규화 재사용
        return DiaryBase._normalize_tags(v)

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "제목 수정",
            "tags": ["work", "project-x"],
        }
    })


class DiaryOut(DiaryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 1,
            "title": "오늘의 기록",
            "content": "점심에 파스타 먹음. 운동 30분.",
            "mood": "happy",
            "date": "2025-08-29",
            "is_private": True,
            "tags": ["food", "exercise"],
            "created_at": "2025-08-29T10:20:30Z",
            "updated_at": "2025-08-29T10:25:00Z",
        }
    })


# --- 검색/정렬용 쿼리 스키마 (미션 3-6) ---
class DiaryQuery(BaseModel):
    q: Optional[str] = Field(None, description="제목/내용 검색어")
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    order: Literal["asc", "desc"] = "desc"
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


# --- 목록 응답(선택: 페이지네이션 메타 포함) ---
class DiaryListOut(BaseModel):
    items: List[DiaryOut]
    total: int
    page: int
    size: int
    has_next: bool
