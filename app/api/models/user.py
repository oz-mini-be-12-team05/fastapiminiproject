from tortoise import fields, models

class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(255, unique=True, index=True)
    name = fields.CharField(50)
    nickname = fields.CharField(100, null=True)
    phone_number = fields.CharField(20, null=True)

    hashed_password = fields.CharField(255)  # ← 이름/길이 수정 권장

    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    is_verified = fields.BooleanField(default=False)
    last_login = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    diaries: fields.ReverseRelation["Diary"]

    class Meta:
        table = "users"

    def __str__(self) -> str:
        return f"<User {self.email}>"
