from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "emotion_keyword" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "token_blacklist" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "jti" VARCHAR(64) NOT NULL UNIQUE,
    "expires_at" TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_token_black_jti_6fe842" ON "token_blacklist" ("jti");
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "username" VARCHAR(50) NOT NULL UNIQUE,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "is_active" BOOL NOT NULL DEFAULT True
);
CREATE TABLE IF NOT EXISTS "diary" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "content" TEXT NOT NULL,
    "mood" VARCHAR(30),
    "date" DATE NOT NULL,
    "is_private" BOOL NOT NULL DEFAULT True,
    "ai_summary" TEXT,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_diary_user_id_8e5b57" ON "diary" ("user_id", "date");
CREATE INDEX IF NOT EXISTS "idx_diary_user_id_2a33cd" ON "diary" ("user_id", "id");
CREATE TABLE IF NOT EXISTS "notifications" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "body" TEXT,
    "is_read" BOOL NOT NULL DEFAULT False,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "revoked_tokens" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "jti" VARCHAR(64) NOT NULL UNIQUE,
    "expires_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS "idx_revoked_tok_jti_9261cc" ON "revoked_tokens" ("jti");
CREATE INDEX IF NOT EXISTS "idx_revoked_tok_expires_b3eec6" ON "revoked_tokens" ("expires_at");
CREATE TABLE IF NOT EXISTS "tag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_tag_user_id_b8aea9" UNIQUE ("user_id", "name")
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "diary_tag" (
    "diary_id" INT NOT NULL REFERENCES "diary" ("id") ON DELETE CASCADE,
    "tag_id" INT NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_diary_tag_diary_i_47c64b" ON "diary_tag" ("diary_id", "tag_id");
CREATE TABLE IF NOT EXISTS "diary_emotion_keyword" (
    "diary_id" INT NOT NULL REFERENCES "diary" ("id") ON DELETE CASCADE,
    "emotionkeyword_id" INT NOT NULL REFERENCES "emotion_keyword" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_diary_emoti_diary_i_a78008" ON "diary_emotion_keyword" ("diary_id", "emotionkeyword_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
