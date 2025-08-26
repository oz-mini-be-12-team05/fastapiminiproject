# database.py
import os
from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()

async def init_db():
    db_url = (
        f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}"
        f"@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    )
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["models"]}  # models.py 파일 위치
    )
    await Tortoise.generate_schemas()
