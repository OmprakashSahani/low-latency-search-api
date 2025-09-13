from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    k: int = 10
    filters: Optional[Dict[str, Any]] = None
    use_vector: bool = False
    use_lexical: bool = True
    rerank: bool = False

class Hit(BaseModel):
    id: str
    score: float
    snippet: str = ""
    meta: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    hits: List[Hit]
    latency_ms: float
    trace_id: str
