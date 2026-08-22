from datetime import datetime

from pydantic import BaseModel, Field


class Location(BaseModel):
    latitude: float
    longitude: float
    name: str | None = None


class AgriculturalAdvisory(BaseModel):
    messages: list[str]
    label: str = "General forecast-based agricultural advisory"


class CurrentWeather(BaseModel):
    location: Location
    temperature_c: float
    feels_like_c: float
    humidity_percent: float = Field(ge=0, le=100)
    wind_speed_mps: float = Field(ge=0)
    condition: str
    description: str
    rain_probability: float | None = Field(default=None, ge=0, le=100)
    source: str = "OpenWeather"
    agricultural_advisory: AgriculturalAdvisory


class ForecastItem(BaseModel):
    timestamp: datetime
    temperature_c: float
    humidity_percent: float = Field(ge=0, le=100)
    condition: str
    description: str
    rain_probability: float = Field(ge=0, le=100)
    wind_speed_mps: float = Field(ge=0)


class WeatherForecast(BaseModel):
    location: Location
    forecast: list[ForecastItem]
    source: str = "OpenWeather"