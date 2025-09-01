from tortoise import fields, models

class RevokedToken(models.Model):
    id = fields.IntField(pk=True)
    jti = fields.CharField(max_length=64, unique=True, index=True)
    user = fields.ForeignKeyField("models.User", related_name="revoked_tokens", null=True)
    # 토큰 만료 시점(만료 지난 항목은 정리용)
    expires_at = fields.DatetimeField(index=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "revoked_tokens"

    def __str__(self) -> str:
        return f"<RevokedToken {self.jti}>"
