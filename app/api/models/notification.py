# app/api/models/notification.py
from tortoise import models, fields

class Notification(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="notifications")
    title = fields.CharField(100)
    body = fields.TextField(null=True)
    is_read = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "notifications"
