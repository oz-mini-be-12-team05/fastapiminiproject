from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=100)
    nickname = fields.CharField(max_length=100)
    phone_number = fields.CharField(max_length=20, null=True)

    last_login = fields.DatetimeField(null=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    is_active = fields.BooleanField(default=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    diaries: fields.ReverseRelation["Diary"]

    class Meta:
        table = "user"