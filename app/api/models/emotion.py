from tortoise import fields, models

class EmotionKeyword(models.Model):
    id = fields.IntField(pk=True)
    keyword = fields.CharField(max_length=50)
    emotion_type = fields.CharField(max_length=50)

    diaries: fields.ManyToManyRelation["Diary"] = fields.ManyToManyField(
        "models.Diary", related_name="emotion_keywords", through="diary_emotion_keywords"
    )


    class Meta:
        table = "emotion keyword"