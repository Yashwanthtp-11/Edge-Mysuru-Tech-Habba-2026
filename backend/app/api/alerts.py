from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.schemas.alerts import AlertResponse, ContractAlert, ContractAlertResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])
alert_service = AlertService()


@router.get("", response_model=ContractAlertResponse)
async def alerts(
    lat: float | None = Query(None, ge=-90, le=90),
    lon: float | None = Query(None, ge=-180, le=180),
    state: str | None = Query(None, min_length=1, max_length=100),
    district: str | None = Query(None, min_length=1, max_length=100),
    crop: str | None = Query(None, min_length=1, max_length=100),
    type: Literal["weather", "government_notification", "market", "general"] | None = None,
    severity: Literal["info", "warning", "high"] | None = None,
    limit: int = Query(20, ge=1, le=50),
) -> ContractAlertResponse:
    try:
        values = await alert_service.build(lat, lon, state, district, crop)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    filtered = [item for item in values if (type is None or item.type == type) and (severity is None or item.severity == severity)]
    contract_alerts = [
        ContractAlert(
            type="price",
            message=item.message,
            severity={"info": "low", "warning": "medium", "high": "high"}[item.severity],
        )
        for item in filtered
        if item.type == "market"
    ]
    return ContractAlertResponse(alerts=contract_alerts[:limit])


@router.get("/latest", response_model=AlertResponse)
async def latest_alerts(limit: int = Query(20, ge=1, le=50)) -> AlertResponse:
    values = await alert_service.build()
    return AlertResponse(count=min(len(values), limit), alerts=values[:limit])