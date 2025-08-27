# app/models/tag.py

from tortoise import fields
from tortoise.models import Model


class Tag(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class DiaryTag(Model):
    id = fields.IntField(pk=True)
    diary = fields.ForeignKeyField("models.Diary", related_name="diary_tags")
    tag = fields.ForeignKeyField("models.Tag", related_name="diary_tags")
