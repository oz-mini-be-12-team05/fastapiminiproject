from tortoise import fields
from tortoise.models import Model

class Diary(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="diaries")
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    ai_summary = fields.TextField(null=True)
    main_emotion = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
