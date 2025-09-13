from fastapi import APIRouter, HTTPException

from ..core.models import SearchRequest, SearchResponse
from ..core.planner import plan_query

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def search_endpoint(req: SearchRequest) -> SearchResponse:
    try:
        return await plan_query(req)
    except Exception as e:  # noqa: BLE001 - broad catch is OK at API boundary
        raise HTTPException(status_code=500, detail=str(e)) from e
