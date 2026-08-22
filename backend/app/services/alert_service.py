import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any

from app.schemas.alerts import Alert
from app.schemas.market import MarketPrice
from app.schemas.notification import Notification
from app.schemas.weather import ForecastItem
from app.services.market_service import MarketService, MarketServiceError
from app.services.notifications_service import NotificationService, NotificationServiceError
from app.services.weather_service import WeatherService, WeatherServiceError


class AlertService:
    def __init__(
        self,
        weather_service: WeatherService | None = None,
        notification_service: NotificationService | None = None,
        market_service: MarketService | None = None,
    ) -> None:
        self.weather_service = weather_service or WeatherService()
        self.notification_service = notification_service or NotificationService()
        self.market_service = market_service or MarketService()

    @staticmethod
    def _id(alert_type: str, source: str, event_id: str) -> str:
        value = f"{alert_type}:{source}:{event_id}".encode("utf-8")
        return hashlib.sha256(value).hexdigest()[:24]

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _alert(
        self,
        alert_type: str,
        severity: str,
        title: str,
        message: str,
        source: str,
        event_id: str,
        official_url: Any = None,
        ttl_hours: float | None = None,
        is_new: bool = True,
    ) -> Alert:
        created_at = self._now()
        return Alert(
            id=self._id(alert_type, source, event_id),
            type=alert_type,
            severity=severity,
            title=title,
            message=message,
            source=source,
            official_url=official_url,
            created_at=created_at,
            expires_at=created_at + timedelta(hours=ttl_hours) if ttl_hours else None,
            is_new=is_new,
        )

    def _weather_alerts(self, forecast: list[ForecastItem]) -> list[Alert]:
        rain_threshold = float(os.getenv("ALERT_RAIN_THRESHOLD_PERCENT", "70"))
        heat_threshold = float(os.getenv("ALERT_HEAT_THRESHOLD_C", "35"))
        wind_threshold = float(os.getenv("ALERT_WIND_THRESHOLD_MPS", os.getenv("WEATHER_WIND_THRESHOLD_MPS", "10")))
        alerts = []
        for item in forecast:
            if item.rain_probability >= rain_threshold:
                severity = "high" if item.rain_probability >= 85 else "warning"
                alerts.append(self._alert(
                    "weather", severity, "Rainfall risk detected",
                    "High rainfall probability detected. Consider delaying irrigation and monitor field drainage.",
                    "OpenWeather", f"rain:{item.timestamp.isoformat()}", ttl_hours=24,
                ))
            if item.temperature_c >= heat_threshold:
                alerts.append(self._alert(
                    "weather", "warning", "High temperature detected",
                    "High temperature conditions detected. Monitor crop water requirements and irrigation needs.",
                    "OpenWeather", f"heat:{item.timestamp.isoformat()}", ttl_hours=24,
                ))
            if item.wind_speed_mps >= wind_threshold:
                alerts.append(self._alert(
                    "weather", "warning", "Strong wind detected",
                    "Strong winds detected. Protect vulnerable crops and structures.",
                    "OpenWeather", f"wind:{item.timestamp.isoformat()}", ttl_hours=24,
                ))
        return alerts

    def _notification_alerts(self, notifications: list[Notification]) -> list[Alert]:
        threshold = int(os.getenv("ALERT_NOTIFICATION_RELEVANCE_THRESHOLD", "60"))
        alerts = []
        for item in notifications:
            if item.relevance_score < threshold or not (item.is_new or item.is_current):
                continue
            alerts.append(self._alert(
                "government_notification", "info", item.title,
                item.summary or "A relevant government notification was detected. Verify current details on the official source.",
                item.source_name, item.id, item.official_url, ttl_hours=72, is_new=item.is_new,
            ))
        return alerts

    def _market_alerts(self, prices: list[MarketPrice]) -> list[Alert]:
        if len(prices) < 2:
            return []
        values = [item.price for item in prices]
        low, high = min(values), max(values)
        if low <= 0 or (high - low) / low < float(os.getenv("ALERT_MARKET_CHANGE_RATIO", "0.20")):
            return []
        reference = max(prices, key=lambda item: item.price)
        return [self._alert(
            "market", "info", "Market price difference detected",
            f"Available official market records show a price difference for {reference.crop}. Compare current local prices before making a decision.",
            reference.source, f"{reference.crop}:{low}:{high}", reference.official_url, ttl_hours=24,
        )]

    async def build(
        self,
        latitude: float | None = None,
        longitude: float | None = None,
        state: str | None = None,
        district: str | None = None,
        crop: str | None = None,
    ) -> list[Alert]:
        alerts: list[Alert] = []
        if (latitude is None) != (longitude is None):
            raise ValueError("lat and lon must be provided together")
        if latitude is not None and longitude is not None:
            try:
                forecast = await self.weather_service.forecast(latitude, longitude)
                alerts.extend(self._weather_alerts(forecast.forecast))
            except WeatherServiceError:
                pass
        try:
            notifications = await self.notification_service.list_notifications(limit=50)
            alerts.extend(self._notification_alerts(notifications))
        except NotificationServiceError:
            pass
        if crop or state or district:
            try:
                prices = await self.market_service.fetch(crop=crop, market=None, district=district, limit=50)
                alerts.extend(self._market_alerts(prices))
            except MarketServiceError:
                pass
        unique = {item.id: item for item in alerts}
        return [item for item in unique.values() if not item.expires_at or item.expires_at > self._now()]