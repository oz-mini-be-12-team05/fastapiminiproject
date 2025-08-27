from fastapi import FastAPI
from app.api.db.database import init_db  # 아래에서 작성할 database.py
import uvicorn

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI + Tortoise + asyncpg!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
