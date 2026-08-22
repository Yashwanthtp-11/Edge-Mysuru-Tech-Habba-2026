import re

from app.schemas.notification import NotificationCategory

KEYWORDS = {
    "subsidy": ("subsidy", "subsidies", "benefit"),
    "insurance": ("pmfby", "crop insurance", "insurance"),
    "fertilizer": ("fertilizer", "fertiliser", "urea"),
    "market": ("msp", "procurement", "market price", "mandi"),
    "scheme": ("pm-kisan", "pmkisan", "scheme", "kisan credit"),
    "agriculture": (
        "farmer", "farmers", "agriculture", "agricultural", "crop", "irrigation",
        "agri", "horticulture", "livestock", "seed", "soil",
    ),
}


def classify_notification(title: str, summary: str | None = None) -> tuple[NotificationCategory, int]:
    text = f"{title} {summary or ''}".lower()
    score = min(100, sum(18 if re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) else 0 for words in KEYWORDS.values() for word in words))
    if score == 0:
        return "other", 0
    for category in ("subsidy", "insurance", "fertilizer", "market", "scheme", "agriculture"):
        if any(word in text for word in KEYWORDS[category]):
            return category, score
    return "farmer_notice", score