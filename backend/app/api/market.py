from fastapi import APIRouter, HTTPException, Query

from app.schemas.market import MarketPriceResponse
from app.services.market_service import MarketService, MarketServiceError, SOURCE_NAME

router = APIRouter(prefix="/market", tags=["market"])
market_service = MarketService()


@router.get("/prices", response_model=MarketPriceResponse)
async def market_prices(
    crop: str | None = Query(None, min_length=1, max_length=100),
    market: str | None = Query(None, min_length=1, max_length=100),
    district: str | None = Query(None, min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=50),
) -> MarketPriceResponse:
    try:
        prices = await market_service.fetch(crop, market, district, limit)
    except MarketServiceError as error:
        raise HTTPException(status_code=error.status_code, detail={"code": error.code, "message": error.message}) from error
    return MarketPriceResponse(count=len(prices), source=SOURCE_NAME, prices=prices)