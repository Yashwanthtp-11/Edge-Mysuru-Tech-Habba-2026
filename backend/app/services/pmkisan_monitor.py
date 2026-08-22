import hashlib
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

PMKISAN_URL = "https://pmkisan.gov.in/"
SOURCE_NAME = "PM-KISAN official portal"


class PublicLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.current_href: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.current_href = dict(attrs).get("href")
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.current_href:
            text = " ".join("".join(self.current_text).split())
            self.links.append((self.current_href, text))
            self.current_href = None


def parse_pmkisan_page(
    html: str,
    base_url: str = PMKISAN_URL,
    detected_at: datetime | None = None,
    keywords: tuple[str, ...] = ("notice", "update", "press", "installment", "kisan"),
) -> list[dict]:
    parser = PublicLinkParser()
    parser.feed(html)
    detected = detected_at or datetime.now(timezone.utc)
    results = []
    for href, title in parser.links:
        text = f"{title} {href}".lower()
        if not title or not any(word in text for word in keywords):
            continue
        url = urljoin(base_url, href)
        base_host = base_url.split("//", 1)[-1].split("/", 1)[0]
        if not url.startswith((f"https://{base_host}/", f"http://{base_host}/")):
            continue
        clean_title = re.sub(r"\s+", " ", title).strip()
        results.append({
            "id": hashlib.sha256(url.encode("utf-8")).hexdigest()[:24],
            "title": clean_title,
            "summary": None,
            "published_at": None,
            "detected_at": detected,
            "source_name": SOURCE_NAME,
            "source_type": "official_portal",
            "official_url": url,
        })
    return results


async def fetch_pmkisan_updates(client: httpx.AsyncClient) -> list[dict]:
    response = await client.get(PMKISAN_URL)
    response.raise_for_status()
    return parse_pmkisan_page(response.text)