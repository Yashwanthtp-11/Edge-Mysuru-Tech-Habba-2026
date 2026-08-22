import asyncio
from datetime import datetime, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import weather as weather_api
from app.main import app
from app.schemas.weather import AgriculturalAdvisory, CurrentWeather, ForecastItem, Location, WeatherForecast
from app.services.weather_service import WeatherService, WeatherServiceError, generate_advisory

client = TestClient(app)
NOW = datetime.now(timezone.utc)

CURRENT_PAYLOAD = {
    "name": "Mysuru",
    "main": {"temp": 28.4, "feels_like": 30.1, "humidity": 72},
    "wind": {"speed": 3.2},
    "weather": [{"main": "Clouds", "description": "scattered clouds"}],
}


@pytest.fixture(autouse=True)
def configured_test_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")


def mock_client(payload: object = CURRENT_PAYLOAD, status_code: int = 200) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=payload, request=request)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_current_weather_is_normalized() -> None:
    service = WeatherService(client=mock_client())

    result = asyncio.run(service.current(12.2958, 76.6394))

    assert result.location.latitude == 12.2958
    assert result.temperature_c == 28.4
    assert result.humidity_percent == 72
    assert result.wind_speed_mps == 3.2
    assert result.condition == "Clouds"
    assert result.source == "OpenWeather"
    assert result.agricultural_advisory.messages == ["Weather conditions are currently moderate."]


def test_forecast_converts_probability_deduplicates_and_sorts() -> None:
    payload = {
        "list": [
            {
                "dt": 1_700_000_600,
                "main": {"temp": 29, "humidity": 70},
                "wind": {"speed": 2},
                "pop": 0.75,
                "weather": [{"main": "Rain", "description": "light rain"}],
            },
            {
                "dt": 1_700_000_000,
                "main": {"temp": 28, "humidity": 65},
                "wind": {"speed": 1},
                "pop": 0,
                "weather": [{"main": "Clouds", "description": "few clouds"}],
            },
            {
                "dt": 1_700_000_600,
                "main": {"temp": 29, "humidity": 70},
                "wind": {"speed": 2},
                "pop": 0.75,
                "weather": [{"main": "Rain", "description": "light rain"}],
            },
        ]
    }
    service = WeatherService(client=mock_client(payload))

    result = asyncio.run(service.forecast(12.2958, 76.6394))

    assert len(result.forecast) == 2
    assert result.forecast[0].timestamp < result.forecast[1].timestamp
    assert result.forecast[1].rain_probability == 75
    assert all(0 <= item.humidity_percent <= 100 for item in result.forecast)


def test_invalid_coordinates_are_rejected() -> None:
    assert client.get("/api/weather/current?lat=91&lon=76").status_code == 422
    assert client.get("/api/weather/current?lat=12&lon=181").status_code == 422


def test_missing_api_key_is_clear_and_does_not_call_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENWEATHER_API_KEY", raising=False)
    service = WeatherService(client=mock_client())

    with pytest.raises(WeatherServiceError) as error:
        asyncio.run(service.current(12, 76))

    assert error.value.status_code == 503
    assert error.value.code == "WEATHER_CONFIGURATION_ERROR"
    assert "appid" not in error.value.message.lower()


def test_provider_timeout_is_mapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    async def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("provider timeout", request=request)

    weather_api.weather_service = WeatherService(
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    )
    response = client.get("/api/weather/current?lat=12&lon=76")

    assert response.status_code == 504
    assert response.json()["detail"]["code"] == "WEATHER_PROVIDER_TIMEOUT"
    assert "test-key" not in response.text


def test_provider_error_and_rate_limit_are_mapped(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")
    weather_api.weather_service = WeatherService(client=mock_client({}, 500))
    provider_error = client.get("/api/weather/current?lat=12&lon=76")
    weather_api.weather_service = WeatherService(client=mock_client({}, 429))
    rate_limit = client.get("/api/weather/current?lat=12&lon=76")

    assert provider_error.status_code == 502
    assert rate_limit.status_code == 429
    assert "test-key" not in provider_error.text + rate_limit.text


def test_invalid_provider_response_is_rejected() -> None:
    service = WeatherService(client=mock_client({"unexpected": True}))

    with pytest.raises(WeatherServiceError) as error:
        asyncio.run(service.current(12, 76))

    assert error.value.status_code == 502
    assert error.value.code == "WEATHER_PROVIDER_INVALID_RESPONSE"


def test_contract_weather_route_reuses_existing_service(monkeypatch: pytest.MonkeyPatch) -> None:
    class WeatherContractStub:
        async def current(self, latitude: float, longitude: float) -> CurrentWeather:
            return CurrentWeather(
                location=Location(latitude=latitude, longitude=longitude),
                temperature_c=28.4,
                feels_like_c=30.1,
                humidity_percent=72,
                wind_speed_mps=3.2,
                condition="Clouds",
                description="scattered clouds",
                rain_probability=None,
                agricultural_advisory=AgriculturalAdvisory(messages=["Weather conditions are currently moderate."]),
            )

        async def forecast(self, latitude: float, longitude: float) -> WeatherForecast:
            return WeatherForecast(
                location=Location(latitude=latitude, longitude=longitude),
                forecast=[ForecastItem(
                    timestamp=NOW,
                    temperature_c=28,
                    humidity_percent=70,
                    condition="Clouds",
                    description="few clouds",
                    rain_probability=20,
                    wind_speed_mps=2,
                )],
            )

    monkeypatch.setattr(weather_api, "weather_service", WeatherContractStub())
    response = client.get("/weather?lat=12&lon=76")
    assert response.status_code == 200
    assert set(response.json()) == {"current", "forecast", "suggestion"}
    assert response.json()["current"] == {"temp": 28.4, "condition": "Clouds", "rain_chance": 0}
    assert response.json()["suggestion"] == "Weather conditions are currently moderate."


@pytest.mark.parametrize(
    ("rain", "temperature", "humidity", "wind", "expected_count"),
    [
        (69, 34.9, 79, 9.9, 1),
        (70, 35, 80, 10, 4),
        (71, 35.1, 80.1, 10.1, 4),
    ],
)
def test_advisory_thresholds_are_deterministic(
    rain: float,
    temperature: float,
    humidity: float,
    wind: float,
    expected_count: int,
) -> None:
    first = generate_advisory(temperature, humidity, rain, wind)
    second = generate_advisory(temperature, humidity, rain, wind)

    assert len(first.messages) == expected_count
    assert first.messages == second.messages