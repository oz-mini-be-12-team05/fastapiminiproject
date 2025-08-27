from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "emotion keyword" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "keyword" VARCHAR(50) NOT NULL,
    "emotion_type" VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS "tag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "email" VARCHAR(255) NOT NULL UNIQUE,
    "password" VARCHAR(100) NOT NULL,
    "nickname" VARCHAR(100) NOT NULL,
    "phone_number" VARCHAR(20),
    "last_login" TIMESTAMPTZ,
    "is_staff" BOOL NOT NULL DEFAULT False,
    "is_superuser" BOOL NOT NULL DEFAULT False,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "diary" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(255) NOT NULL,
    "content" TEXT NOT NULL,
    "ai_summary" TEXT,
    "main_emotion" VARCHAR(50),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "diary_emotion_keywords" (
    "emotion keyword_id" INT NOT NULL REFERENCES "emotion keyword" ("id") ON DELETE CASCADE,
    "diary_id" INT NOT NULL REFERENCES "diary" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_diary_emoti_emotion_c797c7" ON "diary_emotion_keywords" ("emotion keyword_id", "diary_id");
CREATE TABLE IF NOT EXISTS "diary_tags" (
    "tag_id" INT NOT NULL REFERENCES "tag" ("id") ON DELETE CASCADE,
    "diary_id" INT NOT NULL REFERENCES "diary" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_diary_tags_tag_id_696fe9" ON "diary_tags" ("tag_id", "diary_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
