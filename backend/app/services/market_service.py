import os
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

import httpx

from app.schemas.market import MarketPrice

DATA_GOV_BASE_URL = "https://api.data.gov.in/resource"
DEFAULT_TIMEOUT_SECONDS = 10.0
SOURCE_NAME = "data.gov.in / Agmarknet"


class MarketServiceError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _value(record: dict[str, Any], names: tuple[str, ...]) -> Any:
    normalized = {str(key).strip().casefold().replace(" ", "_"): value for key, value in record.items()}
    for name in names:
        value = normalized.get(name.casefold().replace(" ", "_"))
        if value not in (None, ""):
            return value
    return None


def _date_value(value: Any) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    for pattern in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(str(value), pattern).date()
        except ValueError:
            continue
    return None


def normalize_market_record(record: Any, official_url: str) -> MarketPrice:
    if not isinstance(record, dict):
        raise ValueError("Market record is not an object")
    crop = _value(record, ("commodity", "crop", "commodity_name"))
    price = _value(record, ("modal_price", "modal_x0020_price", "price", "market_price"))
    if crop in (None, "") or price in (None, ""):
        raise ValueError("Market record is missing crop or price")
    try:
        numeric_price = float(str(price).replace(",", "").strip())
    except (TypeError, ValueError) as error:
        raise ValueError("Market record has invalid price") from error
    if numeric_price < 0:
        raise ValueError("Market record has invalid price")
    return MarketPrice(
        crop=str(crop).strip(),
        market=_value(record, ("market", "market_name")),
        district=_value(record, ("district", "district_name")),
        state=_value(record, ("state", "state_name")),
        price=numeric_price,
        unit=_value(record, ("unit", "price_unit")),
        price_date=_date_value(_value(record, ("arrival_date", "price_date", "date"))),
        source=SOURCE_NAME,
        official_url=official_url,
    )


class MarketService:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        client_factory: Callable[..., httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        self.client = client
        self.client_factory = client_factory

    async def fetch(self, crop: str | None = None, market: str | None = None, district: str | None = None, limit: int = 20) -> list[MarketPrice]:
        api_key = os.getenv("DATA_GOV_API_KEY")
        resource = os.getenv("DATA_GOV_MARKET_RESOURCE")
        if not api_key or not resource:
            raise MarketServiceError(
                "MARKET_SOURCE_NOT_CONFIGURED",
                "Official market price source is not configured.",
                503,
            )
        official_url = f"{DATA_GOV_BASE_URL}/{resource}"
        params = {"api-key": api_key, "format": "json", "limit": limit}
        request_client = self.client or self.client_factory(timeout=DEFAULT_TIMEOUT_SECONDS)
        should_close = self.client is None
        try:
            response = await request_client.get(official_url, params=params)
            if response.status_code == 429:
                raise MarketServiceError("MARKET_SOURCE_RATE_LIMITED", "Market price source rate limit reached. Please try again later.", 429)
            if response.status_code >= 400:
                raise MarketServiceError("MARKET_SOURCE_ERROR", "Official market price source is temporarily unavailable.", 502)
            payload = response.json()
            if not isinstance(payload, dict) or not isinstance(payload.get("records"), list):
                raise ValueError("Invalid market response")
            prices = []
            for record in payload["records"]:
                try:
                    prices.append(normalize_market_record(record, official_url))
                except ValueError:
                    continue
            if not prices and payload["records"]:
                raise ValueError("No valid market records")
            return self._filter(prices, crop, market, district)[:limit]
        except MarketServiceError:
            raise
        except (httpx.TimeoutException, TimeoutError) as error:
            raise MarketServiceError("MARKET_SOURCE_TIMEOUT", "Market price source timed out. Please try again.", 504) from error
        except (httpx.HTTPError, ValueError, TypeError) as error:
            raise MarketServiceError("MARKET_SOURCE_INVALID_RESPONSE", "Market price source returned invalid data.", 502) from error
        finally:
            if should_close:
                await request_client.aclose()

    @staticmethod
    def _filter(prices: list[MarketPrice], crop: str | None, market: str | None, district: str | None) -> list[MarketPrice]:
        if crop:
            crop_key = crop.casefold().strip()
            prices = [item for item in prices if item.crop.casefold().strip() == crop_key]
        if market:
            market_key = market.casefold().strip()
            prices = [item for item in prices if item.market and market_key in item.market.casefold()]
        if district:
            district_key = district.casefold().strip()
            prices = [item for item in prices if item.district and district_key in item.district.casefold()]
        return prices