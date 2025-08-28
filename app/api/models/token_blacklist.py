from tortoise import fields, models

class TokenBlacklist(models.Model):
    id = fields.IntField(pk=True)
    # JWT jti(고유 ID)
    jti = fields.CharField(max_length=64, unique=True, index=True)
    # 이 토큰의 만료 시각 (DB에서 청소할 때 사용)
    expires_at = fields.DatetimeField()

    class Meta:
        table = "token_blacklist"
