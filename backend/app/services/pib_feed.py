import hashlib
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

PIB_RSS_URL = "https://www.pib.gov.in/RssMain.aspx?ModId=6&Lang=2&Regid=3"
PIB_SOURCE_NAME = "Press Information Bureau"


def _text(element: ElementTree.Element | None) -> str | None:
    return " ".join("".join(element.itertext()).split()) if element is not None else None


def _parse_date(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    try:
        return parsedate_to_datetime(value).astimezone(timezone.utc)
    except (TypeError, ValueError, OverflowError):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        except ValueError as error:
            raise ValueError("Invalid RSS publication date") from error


def parse_pib_rss(xml: str, detected_at: datetime | None = None) -> list[dict]:
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError as error:
        raise ValueError("Malformed PIB RSS XML") from error
    detected = detected_at or datetime.now(timezone.utc)
    results = []
    for item in root.findall(".//item"):
        title = _text(item.find("title"))
        link = _text(item.find("link"))
        if not title or not link:
            continue
        guid = _text(item.find("guid")) or link
        summary = _text(item.find("description"))
        date_value = _text(item.find("pubDate")) or _text(item.find("published"))
        published_at = _parse_date(date_value) if date_value else None
        results.append({
            "id": hashlib.sha256(guid.encode("utf-8")).hexdigest()[:24],
            "title": title,
            "summary": summary,
            "published_at": published_at,
            "detected_at": detected,
            "source_name": PIB_SOURCE_NAME,
            "source_type": "official_rss",
            "official_url": link,
        })
    return results


async def fetch_pib_feed(client: httpx.AsyncClient) -> list[dict]:
    response = await client.get(PIB_RSS_URL)
    response.raise_for_status()
    return parse_pib_rss(response.text)