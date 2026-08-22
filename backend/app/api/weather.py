from fastapi import APIRouter, HTTPException, Query

from app.schemas.weather import CurrentWeather, WeatherForecast
from app.services.weather_service import WeatherService, WeatherServiceError

router = APIRouter(prefix="/api/weather", tags=["weather"])
weather_service = WeatherService()


def _provider_error(error: WeatherServiceError) -> HTTPException:
    return HTTPException(
        status_code=error.status_code,
        detail={"code": error.code, "message": error.message},
    )


@router.get("/current", response_model=CurrentWeather)
async def current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
) -> CurrentWeather:
    try:
        return await weather_service.current(lat, lon)
    except WeatherServiceError as error:
        raise _provider_error(error) from error


@router.get("/forecast", response_model=WeatherForecast)
async def weather_forecast(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
) -> WeatherForecast:
    try:
        return await weather_service.forecast(lat, lon)
    except WeatherServiceError as error:
        raise _provider_error(error) from error