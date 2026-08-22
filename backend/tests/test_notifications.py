import asyncio
from datetime import datetime, timedelta, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app.api import notifications as notifications_api
from app.main import app
from app.services.notification_classifier import classify_notification
from app.services.notifications_service import NotificationService
from app.services.pib_feed import parse_pib_rss
from app.services.pmfby_monitor import parse_pmfby_page
from app.services.pmkisan_monitor import parse_pmkisan_page

client = TestClient(app)
NOW = datetime(2026, 8, 22, 12, 0, tzinfo=timezone.utc)
RSS = f"""<?xml version="1.0"?><rss><channel>
<item><guid>one</guid><title>New crop insurance subsidy for farmers</title>
<link>https://www.pib.gov.in/PressReleasePage.aspx?id=1</link>
<description>Official agriculture announcement</description>
<pubDate>Sat, 22 Aug 2026 10:00:00 GMT</pubDate></item>
<item><guid>one</guid><title>Duplicate item</title>
<link>https://www.pib.gov.in/PressReleasePage.aspx?id=1</link>
<pubDate>Sat, 22 Aug 2026 10:00:00 GMT</pubDate></item>
</channel></rss>"""


def test_pib_rss_parsing_and_stable_deduplication() -> None:
    first = parse_pib_rss(RSS, NOW)
    second = parse_pib_rss(RSS, NOW)

    assert len(first) == 2
    assert first[0]["id"] == second[0]["id"]
    assert first[0]["published_at"].year == 2026
    assert first[0]["official_url"].startswith("https://")


@pytest.mark.parametrize("xml", ["<rss>", "<rss><channel></channel></rss>"])
def test_malformed_and_empty_rss(xml: str) -> None:
    if xml == "<rss>":
        with pytest.raises(ValueError):
            parse_pib_rss(xml)
    else:
        assert parse_pib_rss(xml) == []


def test_public_portal_parsers_keep_official_links_and_no_private_data() -> None:
    pmkisan = parse_pmkisan_page(
        '<a href="/notice.html">Important Farmer Notice</a><a href="https://evil.test">Bank account</a>',
        detected_at=NOW,
    )
    pmfby = parse_pmfby_page('<a href="/updates.html">Crop insurance update</a>', detected_at=NOW)

    assert len(pmkisan) == 1
    assert pmkisan[0]["official_url"].startswith("https://pmkisan.gov.in/")
    assert pmkisan[0]["published_at"] is None
    assert len(pmfby) == 1
    assert pmfby[0]["source_name"] == "PMFBY official portal"


def test_classifier_is_deterministic_and_categorizes() -> None:
    category, score = classify_notification("Crop insurance subsidy for farmers")
    assert category == "subsidy"
    assert 0 < score <= 100
    assert classify_notification("Unrelated announcement") == ("other", 0)


def _mock_client(responses: list[httpx.Response]) -> httpx.AsyncClient:
    async def handler(request: httpx.Request) -> httpx.Response:
        response = responses.pop(0)
        response.request = request
        return response

    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


def test_service_cache_new_detection_and_freshness(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOTIFICATION_CACHE_TTL_SECONDS", "3600")
    service = NotificationService(tmp_path / "notification_cache.json", client=_mock_client([
        httpx.Response(200, text=RSS),
        httpx.Response(200, text='<a href="/notice.html">Farmer notice</a>'),
        httpx.Response(200, text='<a href="/updates.html">Crop update</a>'),
    ]))

    first = asyncio.run(service.refresh())
    assert first
    assert all(item.is_new for item in first)
    assert all(item.is_current for item in first if item.published_at)
    assert asyncio.run(service.get_notification(first[0].id)).id == first[0].id


def test_cache_reuse_and_query_filters(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOTIFICATION_CACHE_TTL_SECONDS", "3600")
    service = NotificationService(tmp_path / "notification_cache.json", client=_mock_client([
        httpx.Response(200, text=RSS),
        httpx.Response(200, text=""),
        httpx.Response(200, text=""),
    ]))
    first = asyncio.run(service.list_notifications())
    service.client = None
    assert asyncio.run(service.list_notifications(search="insurance", category="subsidy", limit=1))
    assert len(service.query(first, search="missing", limit=10)) == 0


def test_old_item_is_historical(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NOTIFICATION_FRESHNESS_HOURS", "72")
    service = NotificationService(tmp_path / "cache.json")
    old = {
        "id": "old", "title": "Old farmer notice", "summary": None,
        "published_at": NOW - timedelta(days=5), "detected_at": NOW,
        "source_name": "Test", "source_type": "official_rss",
        "official_url": "https://example.gov/old",
    }

    notification = service._decorate(old, False)

    assert notification.is_current is False
    assert notification.is_new is True


def test_notification_api_unknown_id_and_secret_safety(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    notifications_api.notification_service = NotificationService(tmp_path / "missing.json")
    assert client.get("/notifications/unknown").status_code == 404

    async def unavailable(**filters):
        from app.services.notifications_service import NotificationServiceError
        raise NotificationServiceError("SOURCE_UNAVAILABLE", "Sources unavailable.", 503)

    monkeypatch.setattr(notifications_api.notification_service, "list_notifications", unavailable)
    response = client.get("/notifications?limit=1")
    assert response.status_code == 503
    assert "DATA_GOV_API_KEY" not in response.text
    assert "secret" not in response.text.lower()