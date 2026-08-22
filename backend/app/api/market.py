from fastapi import APIRouter, HTTPException, Query

from app.schemas.market import ContractMarketPrice, ContractMarketPriceResponse
from app.services.market_service import MarketService, MarketServiceError

router = APIRouter(prefix="/market", tags=["market"])
market_service = MarketService()


@router.get("/prices", response_model=ContractMarketPriceResponse)
async def market_prices(
    crop: str = Query(..., min_length=1, max_length=100),
    market: str | None = Query(None, min_length=1, max_length=100),
    district: str | None = Query(None, min_length=1, max_length=100),
    limit: int = Query(20, ge=1, le=50),
) -> ContractMarketPriceResponse:
    try:
        prices = await market_service.fetch(crop, market, district, limit)
    except MarketServiceError as error:
        raise HTTPException(status_code=error.status_code, detail={"code": error.code, "message": error.message}) from error
    contract_prices = [
        ContractMarketPrice(mandi=item.market, price_per_quintal=item.price)
        for item in prices
        if item.market and item.unit and "quintal" in item.unit.casefold()
    ]
    return ContractMarketPriceResponse(crop=crop, prices=contract_prices)