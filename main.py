import os
import sys
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.schemas import (
    PredictRequest,
    PredictResponse,
    LocationInfo,
    CurrentWeatherInfo,
    RainPredictionData,
    ExplanationResponse,
)
from backend.weather_service import fetch_live_weather_and_history
from backend.prediction_service import prediction_service

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("weather_ai_backend")

app = FastAPI(
    title="Weather & Rainfall AI Prediction API",
    description="Real-time Weather & Rainfall AI Prediction System powered by Open-Meteo & XGBoost ML Models.",
    version="1.0.0"
)

# Enable CORS for React frontend (Vite default port 5173 / 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", summary="Health Check")
def health_check():
    """Returns status of FastAPI backend and ML models readiness."""
    models_ready = prediction_service.is_ready()
    return {
        "status": "healthy",
        "models_loaded": models_ready,
        "api_version": "1.0.0"
    }


@app.get("/weather", summary="Get Current Weather & Open-Meteo Forecast")
def get_weather(latitude: float = Query(..., example=12.2958), longitude: float = Query(..., example=76.6394)):
    """Fetches real-time weather and forecast directly from Open-Meteo API."""
    try:
        df, current_weather = fetch_live_weather_and_history(latitude, longitude)
        return {
            "location": {"latitude": latitude, "longitude": longitude},
            "weather": current_weather
        }
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/rain", summary="Rain Probability & Classification Only")
def predict_rain(req: PredictRequest):
    """Predicts rain probability and binary rain/no-rain outcome using trained XGBoost Classifier."""
    try:
        df, _ = fetch_live_weather_and_history(req.latitude, req.longitude)
        res = prediction_service.predict_current_and_hourly(df)
        pred = res["prediction"]
        return {
            "location": {"latitude": req.latitude, "longitude": req.longitude},
            "rain_probability": pred["rain_probability"],
            "rain_prediction": pred["rain_prediction"],
            "confidence": "HIGH" if abs(pred["rain_probability"] - 50) > 25 else "MEDIUM"
        }
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict", response_model=PredictResponse, summary="Full Rainfall & Weather AI Prediction")
def predict_full(req: PredictRequest):
    """
    Main endpoint for Frontend dashboard.
    Fetches real-time Open-Meteo weather data, runs XGBoost classifier & regressor inference,
    and returns current weather, rainfall prediction (prob, amount mm, risk level), and 24h hourly forecast.
    """
    try:
        logger.info(f"Received prediction request for ({req.latitude}, {req.longitude})")
        df, current_weather = fetch_live_weather_and_history(req.latitude, req.longitude)
        ml_results = prediction_service.predict_current_and_hourly(df)

        pred_data = RainPredictionData(
            rain_probability=ml_results["prediction"]["rain_probability"],
            rain_prediction=ml_results["prediction"]["rain_prediction"],
            expected_rainfall_mm=ml_results["prediction"]["expected_rainfall_mm"],
            risk_level=ml_results["prediction"]["risk_level"],
            open_meteo_probability=ml_results["prediction"]["open_meteo_probability"]
        )

        weather_data = CurrentWeatherInfo(
            temperature=current_weather["temperature"],
            humidity=current_weather["humidity"],
            pressure=current_weather["pressure"],
            wind_speed=current_weather["wind_speed"],
            cloud_cover=current_weather["cloud_cover"],
            timestamp=current_weather["timestamp"]
        )

        return PredictResponse(
            location=LocationInfo(latitude=req.latitude, longitude=req.longitude),
            prediction=pred_data,
            weather=weather_data,
            hourly_forecast=ml_results["hourly_forecast"]
        )
    except Exception as e:
        logger.error(f"Error in /predict: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict/explanation", response_model=ExplanationResponse, summary="SHAP Feature Importance & Explanation")
def predict_explanation(latitude: float = Query(..., example=12.2958), longitude: float = Query(..., example=76.6394)):
    """
    Provides SHAP feature attribution explaining which weather factors (e.g. Humidity, Pressure, Cloud Cover)
    contributed to the current ML prediction.
    """
    try:
        df, _ = fetch_live_weather_and_history(latitude, longitude)
        explanation = prediction_service.get_prediction_explanation(df)
        return ExplanationResponse(
            location=LocationInfo(latitude=latitude, longitude=longitude),
            top_factors=explanation["top_factors"],
            base_probability=explanation["base_probability"]
        )
    except Exception as e:
        logger.error(f"Error generating SHAP explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
