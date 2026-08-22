from typing import Literal

from pydantic import BaseModel, Field


class VisionRecommendation(BaseModel):
    condition: str
    confidence: float = Field(ge=0, le=1)
    what_to_do_now: list[str]
    prevention: list[str]
    treatment_options: list[str]
    recommended_inputs: list[str]
    sources: list[str]


class NearbyInput(BaseModel):
    name: str
    distance_km: float = Field(ge=0)
    address: str
    stock_status: str


class VisionDiagnosis(BaseModel):
    label: str
    confidence: float = Field(ge=0, le=1)
    status: Literal["possible_diagnosis", "low_confidence_fallback"]
    recommendation: VisionRecommendation
    nearby_inputs: list[NearbyInput]
