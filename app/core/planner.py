import time
import uuid

from .models import Hit, SearchRequest, SearchResponse


async def plan_query(req: SearchRequest) -> SearchResponse:
    t0 = time.perf_counter()
    q = req.query.strip()
    k = max(1, min(req.k, 50))
    hits = [
        Hit(
            id=f"doc-{i + 1}",
            score=1.0 - (i * 0.01),
            snippet=f"Stub snippet for '{q}' (result {i + 1})",
            meta={"source": "stub"},
        )
        for i in range(k)
    ]
    return SearchResponse(
        hits=hits,
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        trace_id=str(uuid.uuid4()),
    )
