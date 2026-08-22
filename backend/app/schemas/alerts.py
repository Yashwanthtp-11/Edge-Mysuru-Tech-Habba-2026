from datetime import datetime
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field

AlertType = Literal["weather", "government_notification", "market", "general"]
AlertSeverity = Literal["info", "warning", "high"]


class Alert(BaseModel):
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    source: str
    official_url: AnyHttpUrl | None = None
    created_at: datetime
    expires_at: datetime | None = None
    is_new: bool


class AlertResponse(BaseModel):
    count: int
    alerts: list[Alert]


class ContractAlert(BaseModel):
    type: Literal["disease", "price"]
    message: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"]


class ContractAlertResponse(BaseModel):
    alerts: list[ContractAlert]