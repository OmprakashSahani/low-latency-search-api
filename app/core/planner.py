import time
import uuid

from ..utils.timing import stage_timer
from .models import Hit, SearchRequest, SearchResponse
from .rank_lexical import lexical_topk
from .state import LEX_INDEX


async def plan_query(req: SearchRequest) -> tuple[SearchResponse, dict[str, float]]:
    t0 = time.perf_counter()
    stages: dict[str, float] = {}
    k = max(1, min(req.k, 50))

    hits: list[Hit] = []

    # --- lexical stage
    if req.use_lexical:
        with stage_timer(stages, "lexical_topk"):
            scored = lexical_topk(req.query, k=k)

        with stage_timer(stages, "snippets"):
            for doc_id, score in scored:
                snippet = LEX_INDEX.snippet(doc_id, req.query)
                meta = LEX_INDEX.docs[doc_id].meta
                hits.append(Hit(id=doc_id, score=float(score), snippet=snippet, meta=meta))

    # (vector + fusion would slot here later)

    total_ms = (time.perf_counter() - t0) * 1000.0
    resp = SearchResponse(
        hits=hits[:k],
        latency_ms=total_ms,
        trace_id=str(uuid.uuid4()),
    )
    stages["total"] = total_ms
    return resp, stages
