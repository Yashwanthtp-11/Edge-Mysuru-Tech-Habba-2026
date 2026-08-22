from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, Field


class Scheme(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    level: str | None = None
    state: str | None = None
    category: str | None = None
    description: str | None = None
    benefit: str | None = None
    eligibility: str | None = None
    documents: list[str] | None = None
    application_url: AnyHttpUrl | None = None
    official_source: AnyHttpUrl | None = None
    last_verified: datetime | None = None
    is_current: bool | None = None


class SchemeResponse(BaseModel):
    count: int
    schemes: list[Scheme]
