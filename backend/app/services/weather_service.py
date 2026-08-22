import os
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config.settings import get_openweather_api_key
from app.schemas.weather import (
    AgriculturalAdvisory,
    CurrentWeather,
    ForecastItem,
    Location,
    WeatherForecast,
)

OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
DEFAULT_TIMEOUT_SECONDS = 8.0


class WeatherServiceError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _as_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Invalid weather field: {field}")
    return float(value)


def _required_mapping(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Weather provider returned invalid JSON")
    return payload


def generate_advisory(
    temperature_c: float,
    humidity_percent: float,
    rain_probability: float | None,
    wind_speed_mps: float,
) -> AgriculturalAdvisory:
    messages: list[str] = []
    rainfall_threshold = float(os.getenv("WEATHER_RAIN_THRESHOLD_PERCENT", "70"))
    heat_threshold = float(os.getenv("WEATHER_HEAT_THRESHOLD_C", "35"))
    humidity_threshold = float(os.getenv("WEATHER_HUMIDITY_THRESHOLD_PERCENT", "80"))
    wind_threshold = float(os.getenv("WEATHER_WIND_THRESHOLD_MPS", "10"))

    if rain_probability is not None and rain_probability >= rainfall_threshold:
        messages.append(
            "Heavy rainfall is expected. Consider delaying pesticide application and ensure field drainage."
        )
    if temperature_c >= heat_threshold:
        messages.append(
            "High temperature conditions detected. Monitor crop water requirements and irrigation needs."
        )
    if humidity_percent >= humidity_threshold:
        messages.append(
            "High humidity detected. Monitor crops for fungal disease conditions."
        )
    if wind_speed_mps >= wind_threshold:
        messages.append(
            "Strong winds detected. Protect vulnerable crops and structures."
        )
    if not messages:
        messages.append("Weather conditions are currently moderate.")

    return AgriculturalAdvisory(messages=messages)


class WeatherService:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        client_factory: Callable[..., httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        self.client = client
        self.client_factory = client_factory

    async def _request(self, endpoint: str, latitude: float, longitude: float) -> dict[str, Any]:
        api_key = get_openweather_api_key()
        if not api_key:
            raise WeatherServiceError(
                "WEATHER_CONFIGURATION_ERROR",
                "Weather service is not configured.",
                503,
            )

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric",
        }
        request_client = self.client
        should_close = request_client is None
        if request_client is None:
            request_client = self.client_factory(timeout=DEFAULT_TIMEOUT_SECONDS)

        try:
            response = await request_client.get(f"{OPENWEATHER_BASE_URL}/{endpoint}", params=params)
            if response.status_code == 429:
                raise WeatherServiceError(
                    "WEATHER_RATE_LIMITED",
                    "Weather service rate limit reached. Please try again later.",
                    429,
                )
            if response.status_code >= 400:
                raise WeatherServiceError(
                    "WEATHER_PROVIDER_ERROR",
                    "Weather provider is temporarily unavailable.",
                    502,
                )
            return _required_mapping(response.json())
        except WeatherServiceError:
            raise
        except (httpx.TimeoutException, TimeoutError) as error:
            raise WeatherServiceError(
                "WEATHER_PROVIDER_TIMEOUT",
                "Weather provider timed out. Please try again.",
                504,
            ) from error
        except (httpx.HTTPError, ValueError, TypeError) as error:
            raise WeatherServiceError(
                "WEATHER_PROVIDER_INVALID_RESPONSE",
                "Weather provider returned invalid weather data.",
                502,
            ) from error
        finally:
            if should_close:
                await request_client.aclose()

    async def current(self, latitude: float, longitude: float) -> CurrentWeather:
        try:
            payload = await self._request("weather", latitude, longitude)
            main = _required_mapping(payload["main"])
            wind = _required_mapping(payload["wind"])
            weather = payload["weather"]
            if not isinstance(weather, list) or not weather or not isinstance(weather[0], dict):
                raise ValueError("Invalid weather condition")
            condition = weather[0]
            temperature_c = _as_number(main["temp"], "main.temp")
            feels_like_c = _as_number(main["feels_like"], "main.feels_like")
            humidity_percent = _as_number(main["humidity"], "main.humidity")
            wind_speed_mps = _as_number(wind["speed"], "wind.speed")
            if not 0 <= humidity_percent <= 100 or wind_speed_mps < 0:
                raise ValueError("Invalid weather range")
            result = CurrentWeather(
                location=Location(
                    latitude=latitude,
                    longitude=longitude,
                    name=payload.get("name") if isinstance(payload.get("name"), str) else None,
                ),
                temperature_c=temperature_c,
                feels_like_c=feels_like_c,
                humidity_percent=humidity_percent,
                wind_speed_mps=wind_speed_mps,
                condition=str(condition["main"]),
                description=str(condition["description"]),
                agricultural_advisory=generate_advisory(
                    temperature_c, humidity_percent, None, wind_speed_mps
                ),
            )
            return result
        except WeatherServiceError:
            raise
        except (KeyError, ValueError, TypeError) as error:
            raise WeatherServiceError(
                "WEATHER_PROVIDER_INVALID_RESPONSE",
                "Weather provider returned invalid weather data.",
                502,
            ) from error

    async def forecast(self, latitude: float, longitude: float) -> WeatherForecast:
        try:
            payload = await self._request("forecast", latitude, longitude)
            records = payload["list"]
            if not isinstance(records, list):
                raise ValueError("Invalid forecast list")
            normalized: list[ForecastItem] = []
            seen_timestamps: set[datetime] = set()
            for record in records:
                item = _required_mapping(record)
                main = _required_mapping(item["main"])
                wind = _required_mapping(item["wind"])
                weather = item["weather"]
                if not isinstance(weather, list) or not weather or not isinstance(weather[0], dict):
                    raise ValueError("Invalid forecast condition")
                timestamp = datetime.fromtimestamp(_as_number(item["dt"], "dt"), tz=timezone.utc)
                if timestamp in seen_timestamps:
                    continue
                humidity = _as_number(main["humidity"], "main.humidity")
                wind_speed = _as_number(wind["speed"], "wind.speed")
                rain_probability = _as_number(item.get("pop", 0), "pop") * 100
                if not 0 <= humidity <= 100 or rain_probability < 0 or rain_probability > 100 or wind_speed < 0:
                    raise ValueError("Invalid forecast range")
                condition = weather[0]
                normalized.append(
                    ForecastItem(
                        timestamp=timestamp,
                        temperature_c=_as_number(main["temp"], "main.temp"),
                        humidity_percent=humidity,
                        condition=str(condition["main"]),
                        description=str(condition["description"]),
                        rain_probability=rain_probability,
                        wind_speed_mps=wind_speed,
                    )
                )
                seen_timestamps.add(timestamp)
            normalized.sort(key=lambda item: item.timestamp)
            return WeatherForecast(
                location=Location(latitude=latitude, longitude=longitude),
                forecast=normalized,
            )
        except WeatherServiceError:
            raise
        except (KeyError, ValueError, TypeError, OverflowError) as error:
            raise WeatherServiceError(
                "WEATHER_PROVIDER_INVALID_RESPONSE",
                "Weather provider returned invalid forecast data.",
                502,
            ) from error