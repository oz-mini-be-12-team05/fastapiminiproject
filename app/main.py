# app/main.py
from fastapi import FastAPI
from app.api.v1 import api_router as v1_router
from app.api.db.database import init_db, close_db
from app.api.repositories.token_blacklist_repo import purge_expired

app = FastAPI(title="FastAPI Mini Project")

# ── startup ─────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    await init_db()
    try:
        # 만료된 블랙리스트 먼저 정리 (있어도 되고 없어도 됨)
        await purge_expired()
    except Exception:
        # 실패해도 앱이 뜨도록 무시
        pass

# ── shutdown ────────────────────────────────────────────
@app.on_event("shutdown")
async def on_shutdown() -> None:
    try:
        await close_db()  # close_db가 sync면 await 제거
    except Exception:
        pass

# ── 라우팅 ──────────────────────────────────────────────
app.include_router(v1_router, prefix="/api/v1")

# ── 헬스 체크(선택) ─────────────────────────────────────
@app.get("/")
async def root():
    return {"message": "Hello, FastAPI + Tortoise + asyncpg!"}

# ── 로컬 실행 ───────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)




