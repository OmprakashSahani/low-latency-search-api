import time
import uuid

from .models import Hit, SearchRequest, SearchResponse
from .rank_lexical import lexical_topk
from .state import LEX_INDEX


async def plan_query(req: SearchRequest) -> SearchResponse:
    t0 = time.perf_counter()
    k = max(1, min(req.k, 50))

    hits: list[Hit] = []

    if req.use_lexical:
        scored = lexical_topk(req.query, k=k)
        for doc_id, score in scored:
            snippet = LEX_INDEX.snippet(doc_id, req.query)
            meta = LEX_INDEX.docs[doc_id].meta
            hits.append(Hit(id=doc_id, score=float(score), snippet=snippet, meta=meta))

    # (vector + fusion would slot here later)

    return SearchResponse(
        hits=hits[:k],
        latency_ms=(time.perf_counter() - t0) * 1000.0,
        trace_id=str(uuid.uuid4()),
    )
