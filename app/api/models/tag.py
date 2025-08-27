from tortoise import fields, models

class Tag(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)

    diaries: fields.ManyToManyRelation["Diary"] = fields.ManyToManyField(
        "models.Diary", related_name="tags", through="diary_tags"
    )
    class Meta:
        table = "tag"