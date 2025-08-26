from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP INDEX IF EXISTS "uid_user_usernam_9987ab";
        CREATE TABLE IF NOT EXISTS "diary" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "title" VARCHAR(100) NOT NULL,
    "content" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "notification" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "message" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "read" BOOL NOT NULL DEFAULT False,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "tag" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(50) NOT NULL UNIQUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
        ALTER TABLE "user" ADD "name" VARCHAR(50) NOT NULL;
        ALTER TABLE "user" ADD "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
        ALTER TABLE "user" DROP COLUMN "username";
        ALTER TABLE "user" ALTER COLUMN "email" TYPE VARCHAR(100) USING "email"::VARCHAR(100);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" ADD "username" VARCHAR(50) NOT NULL UNIQUE;
        ALTER TABLE "user" DROP COLUMN "name";
        ALTER TABLE "user" DROP COLUMN "created_at";
        ALTER TABLE "user" ALTER COLUMN "email" TYPE VARCHAR(255) USING "email"::VARCHAR(255);
        DROP TABLE IF EXISTS "diary";
        DROP TABLE IF EXISTS "notification";
        DROP TABLE IF EXISTS "tag";
        CREATE UNIQUE INDEX IF NOT EXISTS "uid_user_usernam_9987ab" ON "user" ("username");"""
