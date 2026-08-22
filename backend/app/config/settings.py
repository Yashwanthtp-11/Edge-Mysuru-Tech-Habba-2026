import os

from dotenv import load_dotenv

load_dotenv()


def get_frontend_origin() -> str:
    return os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")


def get_openweather_api_key() -> str | None:
    return os.getenv("OPENWEATHER_API_KEY") or None