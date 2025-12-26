from fastapi import APIRouter, Depends, status
from src.api.schemas.event import DetectionEvent
from src.api.storage.event_store import log_event
from src.middleware.jwt import verify_token

router = APIRouter(tags=["Events"])

@router.post("/log-event", status_code=status.HTTP_201_CREATED)
async def create_log_event(
    event: DetectionEvent,
    user=Depends(verify_token)
):
    event_data = event.dict()
    event_data["user_id"] = user.get("sub")

    log_event(event_data)

    return {"message": "Event logged successfully"}
