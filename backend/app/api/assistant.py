from fastapi import APIRouter

from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["assistant"])
assistant_service = AssistantService()


@router.post("/chat", response_model=AssistantChatResponse)
async def chat(request: AssistantChatRequest) -> AssistantChatResponse:
    return await assistant_service.chat(request)
