from datetime import datetime
from typing import Literal

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
    status: Literal["upcoming", "ongoing", "expired"] | None = None
    crop: str | None = None
    summary: str | None = None


class SchemeResponse(BaseModel):
    count: int
    schemes: list[Scheme]


class SubsidyContract(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    status: Literal["upcoming", "ongoing", "expired"]
    crop: str = Field(min_length=1)
    summary: str = Field(min_length=1)


class SubsidyContractResponse(BaseModel):
    subsidies: list[SubsidyContract]
