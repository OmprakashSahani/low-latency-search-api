from fastapi import APIRouter

from ..core.state import LEX_INDEX

router = APIRouter()


@router.post("/warmup")
async def warmup() -> dict[str, int]:
    _ = LEX_INDEX.avgdl  # touch cached metric
    return {"docs": len(LEX_INDEX.docs)}
