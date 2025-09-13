from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from ..core.state import LEX_INDEX

router = APIRouter()


class IngestDoc(BaseModel):
    id: str
    text: str
    meta: dict[str, Any] | None = None


class IngestBatch(BaseModel):
    docs: list[IngestDoc]


@router.post("/index")
async def index_docs(batch: IngestBatch) -> dict[str, int]:
    n_before = len(LEX_INDEX.docs)
    for d in batch.docs:
        LEX_INDEX.add(d.id, d.text, d.meta or {})
    n_after = len(LEX_INDEX.docs)
    return {"added": n_after - n_before, "total": n_after}
