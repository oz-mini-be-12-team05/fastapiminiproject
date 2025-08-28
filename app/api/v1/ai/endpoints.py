from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["ai"])

@router.get("/ping")
async def ping():
    return {"ok": True}
