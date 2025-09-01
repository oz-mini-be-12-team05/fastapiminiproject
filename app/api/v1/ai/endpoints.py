from __future__ import annotations
from typing import Any
from datetime import datetime as _dt

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from app.api.core.security import get_current_user
from app.api.schemas import DiaryOut
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

@router.post(
    "/diaries/{diary_id}/summarize",
    response_model=DiaryOut,              # dict 대신 DiaryOut 권장
    summary="일기 내용 AI 요약",
    description=(
        "지정한 일기의 제목/내용을 AI로 요약합니다.\n"
        "- 기본 2문장으로 요약합니다.\n"
        "- `overwrite`가 true면 결과를 DB의 `ai_summary` 필드에 저장합니다."
    ),
)
async def summarize_diary(diary_id: int, user=Depends(get_current_user)):
    diary = await Diary.get_or_none(id=diary_id, user=user)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    diary.ai_summary = await ai.summarize(diary.title or "", diary.content or "")
    await diary.save()
    await diary.fetch_related("tags", "emotion_keywords")
    return _to_diary_dict(diary)

@router.post(
    "/diaries/{diary_id}/analyze",
    response_model=DiaryOut,  # dict 대신 DiaryOut 권장
    summary="일기 감정 분석 & 키워드 추출",
    description=(
        "지정한 일기의 제목/내용을 AI로 분석해 감정(main_emotion)과 키워드(emotion_keywords)를 추출합니다.\n"
        "- 기본은 기존 키워드/결과를 덮어씁니다(overwrite=true).\n"
        "- overwrite=false로 주면 기존 키워드에 합쳐 저장(중복 제거).\n"
        "- top_k로 저장할 키워드 최대 개수를 지정할 수 있습니다."
    ),
)
async def analyze_diary(
    diary_id: int = Path(..., ge=1, description="분석할 일기의 ID"),
    top_k: int = Query(5, ge=1, le=10, description="추출/저장할 키워드 개수(최대 10)"),
    overwrite: bool = Query(True, description="기존 키워드/감정 결과를 덮어쓸지 여부"),
    user=Depends(get_current_user),
):
    diary = await Diary.get_or_none(id=diary_id, user=user)
    if not diary:
        raise HTTPException(status_code=404, detail="Diary not found")

    # 1) AI 분석
    emotion, keywords = await ai.analyze(f"{diary.title}\n{diary.content or ''}")
    diary.main_emotion = emotion
    await diary.save()

    # 2) 키워드 저장 로직
    await diary.fetch_related("emotion_keywords")

    if overwrite:
        await diary.emotion_keywords.clear()

    # 기존 키워드와 병합(중복 제거) + top_k 제한
    existing = {ek.name for ek in diary.emotion_keywords} if not overwrite else set()
    for kw in (keywords or [])[:top_k]:
        if kw and kw not in existing:
            ek, _ = await EmotionKeyword.get_or_create(name=str(kw))
            await diary.emotion_keywords.add(ek)
            existing.add(kw)

    await diary.fetch_related("tags", "emotion_keywords")
    return _to_diary_dict(diary)
