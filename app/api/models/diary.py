from __future__ import annotations
from datetime import date
from tortoise import fields, models

class Diary(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="diaries")

    # 스키마/레포와 맞춘 필드
    title = fields.CharField(max_length=100)
    content = fields.TextField()
    mood = fields.CharField(max_length=30, null=True)     # (= 기존 main_emotion 대체)
    date = fields.DateField(default=date.today)            # 목록 기본 최신순 정렬에 필요
    is_private = fields.BooleanField(default=True)

    # 추가 메타
    ai_summary = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # --- M2M 정의 (실제 필드 선언 필요) ---
    # Tag / EmotionKeyword 모델이 models.* 에 존재해야 합니다.
    tags: fields.ManyToManyRelation["Tag"] = fields.ManyToManyField(
        "models.Tag", related_name="diaries", through="diary_tag"
    )
    emotion_keywords: fields.ManyToManyRelation["EmotionKeyword"] = fields.ManyToManyField(
        "models.EmotionKeyword", related_name="diaries", through="diary_emotion_keyword"
    )

    class Meta:
        table = "diary"
        indexes = (
            ("user_id", "date"),
            ("user_id", "id"),
        )

    def __str__(self) -> str:
        return f"<Diary {self.id} {self.title!r}>"
