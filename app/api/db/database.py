# database.py
from tortoise import Tortoise
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경 변수 불러오기

DB_URL = f"postgres://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}" \
         f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

async def init_db():
    await Tortoise.init(
        db_url=DB_URL,
        modules={"models": ["models"]},  # 모델 모듈 위치 지정
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
