from fastapiminiproject.app.api.db.database import init_db, close_db
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.on_event("shutdown")
async def on_shutdown():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Hello, FastAPI + Tortoise!"}
