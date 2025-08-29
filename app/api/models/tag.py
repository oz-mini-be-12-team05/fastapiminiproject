# app/api/models/tag.py
from tortoise import fields, models

class Tag(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="tags")  # 사용자별 태그
    name = fields.CharField(max_length=50)

    class Meta:
        table = "tag"
        unique_together = (("user_id", "name"),)

    def __str__(self) -> str:
        return f"<Tag {self.id} {self.name!r}>"
