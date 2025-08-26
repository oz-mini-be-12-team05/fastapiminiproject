from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)  # 기본키
    username = fields.CharField(max_length=50, unique=True)
    email = fields.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.username
