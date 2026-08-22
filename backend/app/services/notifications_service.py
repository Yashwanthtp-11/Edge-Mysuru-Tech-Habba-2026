import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

from app.schemas.notification import Notification
from app.services.notification_classifier import classify_notification
from app.services.pib_feed import fetch_pib_feed
from app.services.pmfby_monitor import fetch_pmfby_updates
from app.services.pmkisan_monitor import fetch_pmkisan_updates

DEFAULT_CACHE_PATH = Path(__file__).parents[2] / "data" / "notification_cache.json"
DEFAULT_FRESHNESS_HOURS = 72
DEFAULT_CACHE_TTL_SECONDS = 900
DEFAULT_TIMEOUT_SECONDS = 10.0


class NotificationServiceError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class NotificationService:
    def __init__(self, cache_path: Path = DEFAULT_CACHE_PATH, client: httpx.AsyncClient | None = None) -> None:
        self.cache_path = cache_path
        self.client = client

    def _load_cache(self) -> dict[str, dict[str, Any]]:
        if not self.cache_path.exists():
            return {}
        try:
            payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
        except (OSError, json.JSONDecodeError):
            return {}

    def _cache_is_fresh(self) -> bool:
        if not self.cache_path.exists():
            return False
        try:
            age = datetime.now(timezone.utc) - datetime.fromtimestamp(self.cache_path.stat().st_mtime, timezone.utc)
            return age.total_seconds() < float(os.getenv("NOTIFICATION_CACHE_TTL_SECONDS", DEFAULT_CACHE_TTL_SECONDS))
        except OSError:
            return False

    def _save_cache(self, notifications: dict[str, Notification]) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {notification_id: notification.model_dump(mode="json") for notification_id, notification in notifications.items()}
        self.cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _decorate(self, raw: dict[str, Any], was_seen: bool) -> Notification:
        category, score = classify_notification(raw["title"], raw.get("summary"))
        published_at = raw["published_at"]
        freshness_hours = float(os.getenv("NOTIFICATION_FRESHNESS_HOURS", DEFAULT_FRESHNESS_HOURS))
        is_current = bool(published_at and datetime.now(timezone.utc) - published_at <= timedelta(hours=freshness_hours))
        return Notification(
            **raw,
            category=category,
            is_current=is_current,
            is_new=not was_seen,
            relevance_score=score,
        )

    async def refresh(self) -> list[Notification]:
        cached = self._load_cache()
        existing = {key: Notification.model_validate(value) for key, value in cached.items()}
        request_client = self.client
        should_close = request_client is None
        if request_client is None:
            request_client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS, follow_redirects=True)
        fetched: list[dict[str, Any]] = []
        failures = 0
        try:
            for fetcher in (fetch_pib_feed, fetch_pmkisan_updates, fetch_pmfby_updates):
                try:
                    fetched.extend(await fetcher(request_client))
                except (httpx.HTTPError, ValueError, TypeError):
                    failures += 1
            if not fetched and not existing:
                raise NotificationServiceError(
                    "NOTIFICATION_SOURCES_UNAVAILABLE",
                    "Government notification sources are temporarily unavailable.",
                    503,
                )
            unique_fetched: dict[str, dict[str, Any]] = {}
            for raw in fetched:
                unique_fetched.setdefault(raw["id"], raw)
            for raw in unique_fetched.values():
                existing[raw["id"]] = self._decorate(raw, raw["id"] in existing)
            self._save_cache(existing)
            if failures == 3 and not fetched:
                return list(existing.values())
            return list(existing.values())
        finally:
            if should_close:
                await request_client.aclose()

    def query(
        self,
        notifications: list[Notification],
        category: str | None = None,
        state: str | None = None,
        search: str | None = None,
        limit: int = 20,
    ) -> list[Notification]:
        filtered = notifications
        if category:
            filtered = [item for item in filtered if item.category == category]
        if state:
            filtered = [item for item in filtered if item.state and item.state.casefold() == state.casefold()]
        if search:
            term = search.casefold()
            filtered = [
                item for item in filtered
                if term in " ".join(filter(None, (item.title, item.summary, item.source_name, item.category, item.state))).casefold()
            ]
        return sorted(filtered, key=lambda item: item.published_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)[:limit]

    async def list_notifications(self, **filters: Any) -> list[Notification]:
        if self._cache_is_fresh():
            notifications = [Notification.model_validate(value) for value in self._load_cache().values()]
        else:
            notifications = await self.refresh()
        return self.query(notifications, **filters)

    async def get_notification(self, notification_id: str) -> Notification | None:
        value = self._load_cache().get(notification_id)
        return Notification.model_validate(value) if value else None