from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "revoked_tokens" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "jti" VARCHAR(64) NOT NULL UNIQUE,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT REFERENCES "users" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_revoked_tok_jti_9261cc" ON "revoked_tokens" ("jti");
CREATE INDEX IF NOT EXISTS "idx_revoked_tok_expires_b3eec6" ON "revoked_tokens" ("expires_at");;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "revoked_tokens";"""
