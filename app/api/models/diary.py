from tortoise import fields, models
from app.api.models.user import User

class Diary(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="diaries")

    title = fields.CharField(max_length=255)
    content = fields.TextField()
    ai_summary = fields.TextField(null=True)
    main_emotion = fields.CharField(max_length=50, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    tags: fields.ManyToManyRelation["Tag"]
    emotion_keywords: fields.ManyToManyRelation["EmotionKeyword"]


    class Meta:
        table = "diary"