# app/api/models/emotion_keyword.py
from tortoise import fields, models

class EmotionKeyword(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    class Meta:
        table = "emotion_keyword"

    def __str__(self) -> str:
        return f"<EmotionKeyword {self.id} {self.name!r}>"
