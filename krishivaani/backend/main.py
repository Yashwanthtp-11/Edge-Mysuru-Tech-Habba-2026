import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_ROOT = os.path.join(PROJECT_ROOT, "backend")
for path in (PACKAGE_ROOT, PROJECT_ROOT, BACKEND_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from .routes import vision
from app.api.notifications import router as notifications_router
from app.api.weather import router as weather_router

try:
    from .routes import assistant
except ModuleNotFoundError as error:
    if error.name != "sherpa_onnx":
        raise
    assistant = None

app = FastAPI(title="KrishiVaani Backend API")

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if assistant is not None:
    app.include_router(assistant.router, prefix="/assistant", tags=["Assistant"])
app.include_router(vision.router)
app.include_router(weather_router)
app.include_router(notifications_router)

@app.get("/")
def read_root():
    return {"status": "KrishiVaani Backend is running!"}
