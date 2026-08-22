from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class PredictRequest(BaseModel):
    latitude: float = Field(..., example=12.2958, description="Latitude coordinate")
    longitude: float = Field(..., example=76.6394, description="Longitude coordinate")


class LocationInfo(BaseModel):
    latitude: float
    longitude: float
    city_name: Optional[str] = None


class CurrentWeatherInfo(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    wind_speed: float
    cloud_cover: float
    timestamp: str


class RainPredictionData(BaseModel):
    rain_probability: float = Field(..., description="ML Rain Probability (0 - 100%)")
    rain_prediction: bool = Field(..., description="True if rain expected in next hour")
    expected_rainfall_mm: float = Field(..., description="Predicted rainfall amount in mm")
    risk_level: str = Field(..., description="LOW, MEDIUM, or HIGH risk")
    open_meteo_probability: Optional[float] = Field(None, description="Open-Meteo raw forecast rain probability")


class HourlyForecastItem(BaseModel):
    timestamp: str
    temperature: float
    humidity: float
    precipitation: float
    rain_probability: float


class PredictResponse(BaseModel):
    location: LocationInfo
    prediction: RainPredictionData
    weather: CurrentWeatherInfo
    hourly_forecast: List[HourlyForecastItem]


class FeatureContribution(BaseModel):
    feature: str
    impact_direction: str  # "+" or "-"
    importance_value: float


class ExplanationResponse(BaseModel):
    location: LocationInfo
    top_factors: List[FeatureContribution]
    base_probability: float
