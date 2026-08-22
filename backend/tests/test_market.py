import asyncio

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import market as market_api
from app.main import app
from app.services.market_service import MarketService, MarketServiceError, normalize_market_record

client = TestClient(app)
OFFICIAL_URL = "https://api.data.gov.in/resource/verified-market-resource"
PAYLOAD = {
    "records": [
        {"Commodity": "Tomato", "Market": "Mysuru", "District": "Mysuru", "State": "Karnataka", "Modal Price": "2400", "Arrival_Date": "22/08/2026", "Unit": "Rs/Quintal"},
        {"Commodity": "Onion", "Market": "Mysuru", "District": "Mysuru", "State": "Karnataka", "Modal Price": 1800, "Arrival_Date": "2026-08-22"},
        {"Commodity": "Tomato", "Market": "Bengaluru", "District": "Bengaluru", "State": "Karnataka", "Modal Price": 2600},
    ]
}


@pytest.fixture(autouse=True)
def configured_market_source(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATA_GOV_API_KEY", "test-key")
    monkeypatch.setenv("DATA_GOV_MARKET_RESOURCE", "verified-market-resource")


def mock_client(payload: object = PAYLOAD, status_code: int = 200) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload, request=request)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_normalization_and_valid_market_response() -> None:
    record = normalize_market_record(PAYLOAD["records"][0], OFFICIAL_URL)
    assert record.crop == "Tomato"
    assert record.market == "Mysuru"
    assert record.price == 2400
    assert record.price_date.isoformat() == "2026-08-22"
    assert str(record.official_url) == OFFICIAL_URL


def test_missing_required_fields_are_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_market_record({"Commodity": "Tomato"}, OFFICIAL_URL)
    with pytest.raises(ValueError):
        normalize_market_record({"Commodity": "Tomato", "Modal Price": "unknown"}, OFFICIAL_URL)


def test_filters_are_case_insensitive_and_deterministic() -> None:
    service = MarketService(client=mock_client())
    assert len(asyncio.run(service.fetch(crop="tomato"))) == 2
    assert len(asyncio.run(service.fetch(crop="tomato", market="mysuru"))) == 1
    assert len(asyncio.run(service.fetch(district="BENGALURU"))) == 1


def test_empty_response_is_valid_empty_result() -> None:
    service = MarketService(client=mock_client({"records": []}))
    assert asyncio.run(service.fetch()) == []


def test_invalid_response_is_rejected() -> None:
    service = MarketService(client=mock_client({"data": []}))
    with pytest.raises(MarketServiceError) as error:
        asyncio.run(service.fetch())
    assert error.value.code == "MARKET_SOURCE_INVALID_RESPONSE"


def test_missing_source_configuration_is_clear(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATA_GOV_MARKET_RESOURCE", raising=False)
    with pytest.raises(MarketServiceError) as error:
        asyncio.run(MarketService(client=mock_client()).fetch())
    assert error.value.status_code == 503
    assert "test-key" not in error.value.message


def test_timeout_and_http_error_are_handled() -> None:
    async def timeout_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timeout", request=request)

    timeout_service = MarketService(client=httpx.AsyncClient(transport=httpx.MockTransport(timeout_handler)))
    with pytest.raises(MarketServiceError) as timeout_error:
        asyncio.run(timeout_service.fetch())
    assert timeout_error.value.status_code == 504

    error_service = MarketService(client=mock_client({}, 500))
    with pytest.raises(MarketServiceError) as provider_error:
        asyncio.run(error_service.fetch())
    assert provider_error.value.status_code == 502


def test_route_validation_and_response(monkeypatch: pytest.MonkeyPatch) -> None:
    market_api.market_service = MarketService(client=mock_client())
    response = client.get("/market/prices?crop=tomato&market=Mysuru&limit=1")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["prices"][0]["source"] == "data.gov.in / Agmarknet"
    assert client.get("/market/prices?crop=").status_code == 422
    assert client.get("/market/prices?limit=51").status_code == 422


def test_provider_failures_do_not_expose_credentials() -> None:
    market_api.market_service = MarketService(client=mock_client({}, 500))
    response = client.get("/market/prices")
    assert response.status_code == 502
    assert "test-key" not in response.text