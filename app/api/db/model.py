# models.py
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = "users"
