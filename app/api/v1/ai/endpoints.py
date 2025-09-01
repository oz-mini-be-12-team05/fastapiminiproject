from __future__ import annotations
from typing import Any
from datetime import datetime as _dt

from fastapi import APIRouter, Depends, HTTPException
from app.api.core.security import get_current_user
from app.api.services.ai_provider import ai  # Gemini/Rule-based 자동 선택
from app.api.models.diary import Diary
from app.api.models.emotion import EmotionKeyword

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/ping")
async def ping():
    return {"ok": True}

# 공용: Diary 모델 -> dict 직렬화 (diary/endpoints.py와 동일 컨벤션)
def _to_diary_dict(d) -> dict[str, Any]:
    raw_date = getattr(d, "date", None)
    out_date = raw_date.date() if isinstance(raw_date, _dt) else raw_date
    try:
        tags = [t.name for t in d.tags]
    except Exception:
        tags = []
    try:
        emos = [e.name for e in d.emotion_keywords]
    except Exception:
        emos = []
    return {
        "id": d.id,
        "title": d.title,
        "content": d.content,
        "mood": getattr(d, "mood", None),
        "date": out_date,
        "is_private": getattr(d, "is_private", True),
        "tags": tags,
        "ai_summary": getattr(d, "ai_summary", None),
        "main_emotion": getattr(d, "main_emotion", None),
        "emotion_keywords": emos,
        "created_at": getattr(d, "created_at", None),
        "updated_at": getattr(d, "updated_at", None),
    }

@router.post("/diaries/{diary_id}/summarize", response_model=dict)
async def summarize_diary(diary_id: int, user=Depends(get_current_user)):
    diary = await Diary.get_or_none(id=diary_id, user=user)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    diary.ai_summary = await ai.summarize(diary.title or "", diary.content or "")
    await diary.save()
    await diary.fetch_related("tags", "emotion_keywords")
    return _to_diary_dict(diary)

@router.post("/diaries/{diary_id}/analyze", response_model=dict)
async def analyze_diary(diary_id: int, user=Depends(get_current_user)):
    diary = await Diary.get_or_none(id=diary_id, user=user)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    emotion, keywords = await ai.analyze(f"{diary.title}\n{diary.content}")
    diary.main_emotion = emotion
    await diary.save()

    # 키워드 M2M 갱신
    await diary.fetch_related("emotion_keywords")
    await diary.emotion_keywords.clear()
    for kw in keywords:
        ek, _ = await EmotionKeyword.get_or_create(name=str(kw))
        await diary.emotion_keywords.add(ek)

    await diary.fetch_related("tags", "emotion_keywords")
    return _to_diary_dict(diary)
