# app/api/v1/notify/endpoints.py
from __future__ import annotations  # 선택
from fastapi import APIRouter, Depends, status
from typing import Optional
from pydantic import BaseModel, Field
from app.api.core.security import get_current_user

router = APIRouter(prefix="/notify", tags=["notify"])

class NotificationCreate(BaseModel):
    title: str = Field(..., max_length=100)
    body: Optional[str] = None

class NotificationOut(BaseModel):
    id: int
    title: str
    body: Optional[str] = None
    is_read: bool = False

@router.get("/ping")
async def ping():
    return {"ok": True}

@router.get("", response_model=list[NotificationOut])
async def list_notifications(user=Depends(get_current_user)):
    return []

@router.post("", status_code=status.HTTP_201_CREATED, response_model=NotificationOut)
async def create_notification(payload: NotificationCreate, user=Depends(get_current_user)):
    return NotificationOut(id=1, title=payload.title, body=payload.body)

@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_read(notification_id: int, user=Depends(get_current_user)):
    return NotificationOut(id=notification_id, title="stub", body=None, is_read=True)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(notification_id: int, user=Depends(get_current_user)):
    return
