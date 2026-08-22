from app.services.pmkisan_monitor import parse_pmkisan_page

PMFBY_URL = "https://pmfby.gov.in/"
SOURCE_NAME = "PMFBY official portal"


def parse_pmfby_page(html: str, detected_at=None) -> list[dict]:
    results = parse_pmkisan_page(
        html,
        PMFBY_URL,
        detected_at,
        keywords=("notice", "update", "notification", "insurance", "crop", "pmfby"),
    )
    for result in results:
        result["source_name"] = SOURCE_NAME
    return results


async def fetch_pmfby_updates(client) -> list[dict]:
    response = await client.get(PMFBY_URL)
    response.raise_for_status()
    return parse_pmfby_page(response.text)