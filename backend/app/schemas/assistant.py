from typing import Literal

from pydantic import BaseModel, Field


AssistantLanguage = Literal["kn", "hi", "en"]
AssistantInputType = Literal["voice", "text"]


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1)
    language: AssistantLanguage
    input_type: AssistantInputType
    audio_base64: str | None = None


class AssistantChatResponse(BaseModel):
    reply_text: str
    reply_audio_base64: str
    language: AssistantLanguage
