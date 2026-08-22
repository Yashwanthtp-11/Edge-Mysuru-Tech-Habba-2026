from fastapi import APIRouter, HTTPException, Query

from app.schemas.notification import Notification
from app.services.notifications_service import NotificationService, NotificationServiceError

router = APIRouter(prefix="/notifications", tags=["notifications"])
notification_service = NotificationService()


def _error(error: NotificationServiceError) -> HTTPException:
    return HTTPException(status_code=error.status_code, detail={"code": error.code, "message": error.message})


async def _query_notifications(
    category: str | None,
    state: str | None,
    search: str | None,
    limit: int,
) -> list[Notification]:
    try:
        return await notification_service.list_notifications(category=category, state=state, search=search, limit=limit)
    except NotificationServiceError as error:
        raise _error(error) from error


@router.get("")
async def list_notifications(
    category: str | None = None,
    state: str | None = None,
    search: str | None = None,
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    notifications = await _query_notifications(category, state, search, limit)
    return {"count": len(notifications), "notifications": notifications}


@router.get("/latest")
async def latest_notifications(limit: int = Query(20, ge=1, le=100)) -> dict:
    notifications = await _query_notifications(None, None, None, limit)
    return {"count": len(notifications), "notifications": notifications}


@router.get("/{notification_id}", response_model=Notification)
async def get_notification(notification_id: str) -> Notification:
    notification = await notification_service.get_notification(notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail={"code": "NOTIFICATION_NOT_FOUND", "message": "Notification not found."})
    return notification


@router.post("/refresh")
async def refresh_notifications() -> dict:
    try:
        notifications = await notification_service.refresh()
    except NotificationServiceError as error:
        raise _error(error) from error
    return {"count": len(notifications), "notifications": notifications}