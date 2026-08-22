from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.alerts import router as alerts_router
from app.api.notifications import router as notifications_router
from app.api.market import router as market_router
from app.api.subsidy import router as subsidy_router
from app.api.weather import router as weather_router
from app.config.settings import get_frontend_origin

app = FastAPI(title="KrishiVaani API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_frontend_origin()],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(weather_router)
app.include_router(notifications_router)
app.include_router(market_router)
app.include_router(alerts_router)
app.include_router(subsidy_router)