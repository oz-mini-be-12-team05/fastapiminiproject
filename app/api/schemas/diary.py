# app/api/schemas/diary.py
from __future__ import annotations
from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field

class DiaryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str
    mood: Optional[str] = None
    date: Optional[date] = None
    is_private: bool = True
    tags: List[str] = []

class DiaryCreate(DiaryBase):
    pass

class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    date: Optional[date] = None
    is_private: Optional[bool] = None
    tags: Optional[List[str]] = None

class DiaryOut(DiaryBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
