import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api import alerts as alerts_api
from app.main import app
from app.schemas.market import MarketPrice
from app.schemas.notification import Notification
from app.schemas.weather import ForecastItem, Location, WeatherForecast
from app.services.alert_service import AlertService
from app.services.market_service import MarketServiceError
from app.services.notifications_service import NotificationServiceError
from app.services.weather_service import WeatherServiceError

client = TestClient(app)
NOW = datetime.now(timezone.utc)


def forecast(**changes) -> ForecastItem:
    values = {"temperature_c": 25, "humidity_percent": 60, "rain_probability": 10, "wind_speed_mps": 2}
    values.update(changes)
    return ForecastItem(timestamp=NOW, condition="Clear", description="clear", **values)


class WeatherStub:
    def __init__(self, item: ForecastItem | None = None, fail: bool = False):
        self.item = item
        self.fail = fail

    async def forecast(self, latitude, longitude):
        if self.fail:
            raise WeatherServiceError("WEATHER_UNAVAILABLE", "unavailable", 503)
        return WeatherForecast(location=Location(latitude=latitude, longitude=longitude), forecast=[self.item])


class NotificationStub:
    def __init__(self, items=None, fail=False):
        self.items = items or []
        self.fail = fail

    async def list_notifications(self, **filters):
        if self.fail:
            raise NotificationServiceError("NOTIFICATIONS_UNAVAILABLE", "unavailable", 503)
        return self.items


class MarketStub:
    def __init__(self, items=None, fail=False):
        self.items = items or []
        self.fail = fail

    async def fetch(self, **filters):
        if self.fail:
            raise MarketServiceError("MARKET_UNAVAILABLE", "unavailable", 503)
        return self.items


def service_for(item=None, notifications=None, prices=None, weather_fail=False, market_fail=False):
    return AlertService(
        weather_service=WeatherStub(item or forecast(), weather_fail),
        notification_service=NotificationStub(notifications),
        market_service=MarketStub(prices, market_fail),
    )


def test_weather_threshold_alerts() -> None:
    rain = asyncio.run(service_for(forecast(rain_probability=70)).build(12, 76))
    heavy = asyncio.run(service_for(forecast(rain_probability=85)).build(12, 76))
    heat = asyncio.run(service_for(forecast(temperature_c=35)).build(12, 76))
    wind = asyncio.run(service_for(forecast(wind_speed_mps=10)).build(12, 76))

    assert rain[0].severity == "warning"
    assert heavy[0].severity == "high"
    assert any("temperature" in item.title.lower() for item in heat)
    assert any("wind" in item.title.lower() for item in wind)


def test_normal_weather_has_no_weather_alert() -> None:
    alerts = asyncio.run(service_for(forecast()).build(12, 76))
    assert not [item for item in alerts if item.type == "weather"]


def notification(score=80, is_new=True, is_current=True, notification_id="notice-1") -> Notification:
    return Notification(
        id=notification_id, title="Farmer subsidy update", summary="Official scheme notice",
        published_at=NOW, detected_at=NOW, source_name="Government", source_type="official_rss",
        official_url="https://example.gov/notice", category="subsidy", state=None,
        is_current=is_current, is_new=is_new, relevance_score=score,
    )


def test_government_alert_rules() -> None:
    service = service_for(notifications=[notification()])
    alerts = asyncio.run(service.build())
    assert len(alerts) == 1
    assert alerts[0].type == "government_notification"
    assert alerts[0].official_url
    assert asyncio.run(service_for(notifications=[notification(is_new=False, is_current=False)]).build()) == []
    assert asyncio.run(service_for(notifications=[notification(score=59)]).build()) == []


def market(crop, price, market_name="Mysuru") -> MarketPrice:
    return MarketPrice(crop=crop, market=market_name, district="Mysuru", state="Karnataka", price=price, unit="Rs/Quintal", price_date=None, source="Agmarknet", official_url="https://example.gov/market")


def test_market_alerts_are_safe_and_comparative() -> None:
    assert not asyncio.run(service_for(prices=[], market_fail=True).build(crop="tomato"))
    assert not asyncio.run(service_for(prices=[market("tomato", 100)]).build(crop="tomato"))
    alerts = asyncio.run(service_for(prices=[market("tomato", 100), market("tomato", 150)]).build(crop="tomato"))
    assert len(alerts) == 1
    assert alerts[0].type == "market"
    assert "150" not in alerts[0].message


def test_duplicate_suppression_and_expiration() -> None:
    service = service_for(notifications=[notification(notification_id="same"), notification(notification_id="same")])
    alerts = asyncio.run(service.build())
    assert len(alerts) == 1
    assert alerts[0].expires_at is not None
    assert alerts[0].expires_at > alerts[0].created_at
    duplicate_ids = {item.id for item in alerts}
    assert len(duplicate_ids) == 1


def test_provider_failures_and_missing_coordinates_skip_weather() -> None:
    assert not [item for item in asyncio.run(service_for(weather_fail=True).build(12, 76)) if item.type == "weather"]
    with pytest.raises(ValueError):
        asyncio.run(service_for().build(12, None))


def test_endpoint_filters_and_validation(monkeypatch: pytest.MonkeyPatch) -> None:
    alerts_api.alert_service = service_for(forecast(rain_probability=90))
    assert client.get("/alerts?lat=12&lon=76&type=weather&severity=high&limit=1").status_code == 200
    assert client.get("/alerts?type=unknown").status_code == 422
    assert client.get("/alerts?severity=urgent").status_code == 422
    assert client.get("/alerts?limit=51").status_code == 422
    assert client.get("/alerts?lat=12").status_code == 422