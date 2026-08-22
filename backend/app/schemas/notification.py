from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field

NotificationCategory = Literal[
    "scheme",
    "subsidy",
    "farmer_notice",
    "agriculture",
    "insurance",
    "fertilizer",
    "market",
    "other",
]


class Notification(BaseModel):
    id: str
    title: str = Field(min_length=1)
    summary: str | None = None
    published_at: datetime | None = None
    updated_at: datetime | None = None
    detected_at: datetime
    source_name: str
    source_type: Literal["official_rss", "official_portal"]
    official_url: AnyHttpUrl
    category: NotificationCategory
    state: str | None = None
    is_current: bool
    is_new: bool
    relevance_score: int = Field(ge=0, le=100)