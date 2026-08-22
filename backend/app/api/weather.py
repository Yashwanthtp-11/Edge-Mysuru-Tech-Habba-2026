from fastapi import APIRouter, HTTPException, Query

from app.schemas.weather import CurrentWeather, WeatherContractResponse, WeatherForecast
from app.services.weather_service import WeatherService, WeatherServiceError

router = APIRouter(prefix="/api/weather", tags=["weather"])
contract_router = APIRouter(prefix="/weather", tags=["weather"])
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


@contract_router.get("", response_model=WeatherContractResponse)
async def weather_contract(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
) -> WeatherContractResponse:
    try:
        current = await weather_service.current(lat, lon)
        forecast = await weather_service.forecast(lat, lon)
    except WeatherServiceError as error:
        raise _provider_error(error) from error
    suggestion = current.agricultural_advisory.messages[0]
    return WeatherContractResponse(
        current={
            "temp": current.temperature_c,
            "condition": current.condition,
            "rain_chance": current.rain_probability or 0,
        },
        forecast=forecast.forecast,
        suggestion=suggestion,
    )