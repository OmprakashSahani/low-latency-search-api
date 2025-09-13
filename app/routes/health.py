import time
from typing import TypedDict

from fastapi import APIRouter


class Healthz(TypedDict):
    status: str
    ts: float


router = APIRouter()


@router.get("/healthz")
async def healthz() -> Healthz:
    return {"status": "ok", "ts": time.time()}
