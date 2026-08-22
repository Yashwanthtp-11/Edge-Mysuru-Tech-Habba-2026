from fastapi import APIRouter, HTTPException, Query

from app.schemas.subsidy import Scheme, SubsidyContractResponse
from app.services.subsidy_service import SubsidyService

router = APIRouter(prefix="/subsidy", tags=["subsidy"])
subsidy_service = SubsidyService()


@router.get("/list", response_model=SubsidyContractResponse)
async def list_schemes(
    search: str | None = Query(None, min_length=1, max_length=100),
    category: str | None = Query(None, min_length=1, max_length=100),
    state: str | None = Query(None, min_length=1, max_length=100),
    level: str | None = Query(None, min_length=1, max_length=50),
    is_current: bool | None = None,
    limit: int = Query(20, ge=1, le=100),
) -> SubsidyContractResponse:
    schemes = subsidy_service.list_contract_schemes(search, category, state, level, is_current, limit)
    return SubsidyContractResponse(subsidies=schemes)


@router.get("/{scheme_id}", response_model=Scheme)
async def get_scheme(scheme_id: str) -> Scheme:
    scheme = subsidy_service.get_scheme(scheme_id)
    if scheme is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "SCHEME_NOT_FOUND", "message": "Scheme not found."},
        )
    return scheme
