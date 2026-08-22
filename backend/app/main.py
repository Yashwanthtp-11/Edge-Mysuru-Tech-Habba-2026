from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.notifications import router as notifications_router
from app.api.weather import router as weather_router
from app.api.assistant import router as assistant_router
from app.config.settings import get_frontend_origin

app = FastAPI(title="KrishiVaani API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[get_frontend_origin()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(weather_router)
app.include_router(notifications_router)
app.include_router(assistant_router, prefix="/api/assistant", tags=["Assistant"])