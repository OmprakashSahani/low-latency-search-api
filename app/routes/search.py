from fastapi import APIRouter, HTTPException, Response

from ..core.models import SearchRequest, SearchResponse
from ..core.planner import plan_query

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_endpoint(req: SearchRequest, response: Response) -> SearchResponse:
    try:
        result, stages = await plan_query(req)

        # Add budget/timing headers
        # Compact “X-Compute” with key=ms pairs (rounded).
        compute_header = ",".join(f"{k}={round(v, 3)}ms" for k, v in stages.items() if k != "total")
        response.headers["X-Latency-Total-ms"] = str(
            round(stages.get("total", result.latency_ms), 3)
        )
        if compute_header:
            response.headers["X-Compute"] = compute_header
        response.headers["Trace-Id"] = result.trace_id

        return result
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(e)) from e
