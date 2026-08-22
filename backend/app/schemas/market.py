from datetime import date

from pydantic import AnyHttpUrl, BaseModel, Field


class MarketPrice(BaseModel):
    crop: str
    market: str | None = None
    district: str | None = None
    state: str | None = None
    price: float
    unit: str | None = None
    price_date: date | None = None
    source: str
    official_url: AnyHttpUrl


class MarketPriceResponse(BaseModel):
    count: int
    source: str
    prices: list[MarketPrice]