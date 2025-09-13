from fastapi import APIRouter
import time

router = APIRouter()

@router.get("/healthz")
async def healthz():
    return {"status": "ok", "ts": time.time()}
