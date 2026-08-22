from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse


class DevelopmentAssistantAdapter:
    async def respond(self, request: AssistantChatRequest) -> AssistantChatResponse:
        return AssistantChatResponse(
            reply_text="Development assistant stub is active.",
            reply_audio_base64="",
            language=request.language,
        )


class AssistantService:
    def __init__(self, adapter: DevelopmentAssistantAdapter | None = None) -> None:
        self.adapter = adapter or DevelopmentAssistantAdapter()

    async def chat(self, request: AssistantChatRequest) -> AssistantChatResponse:
        return await self.adapter.respond(request)
