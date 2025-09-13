from typing import Any

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    k: int = 10
    filters: dict[str, Any] | None = None
    use_vector: bool = False
    use_lexical: bool = True
    rerank: bool = False


class Hit(BaseModel):
    id: str
    score: float
    snippet: str = ""
    meta: dict[str, Any] = {}


class SearchResponse(BaseModel):
    hits: list[Hit]
    latency_ms: float
    trace_id: str
