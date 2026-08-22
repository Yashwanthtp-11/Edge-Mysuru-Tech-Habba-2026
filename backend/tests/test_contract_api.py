from fastapi.testclient import TestClient

from app.api import assistant as assistant_api
from app.api import vision as vision_api
from app.main import app
from app.schemas.assistant import AssistantChatRequest, AssistantChatResponse
from app.schemas.vision import VisionDiagnosis

client = TestClient(app)


def test_assistant_text_contract_and_deterministic_stub() -> None:
    payload = {"message": "How is my crop?", "language": "en", "input_type": "text", "audio_base64": None}
    first = client.post("/assistant/chat", json=payload)
    second = client.post("/assistant/chat", json=payload)
    assert first.status_code == 200
    assert set(first.json()) == {"reply_text", "reply_audio_base64", "language"}
    assert first.json() == second.json()
    assert first.json()["language"] == "en"


def test_assistant_voice_contract() -> None:
    response = client.post(
        "/assistant/chat",
        json={"message": "hello", "language": "kn", "input_type": "voice", "audio_base64": "AA=="},
    )
    assert response.status_code == 200
    assert response.json()["reply_audio_base64"] == ""
    assert response.json()["language"] == "kn"


def test_assistant_language_validation() -> None:
    response = client.post(
        "/assistant/chat",
        json={"message": "hello", "language": "fr", "input_type": "text", "audio_base64": None},
    )
    assert response.status_code == 422


def test_assistant_service_boundary_is_replaceable() -> None:
    class Adapter:
        async def respond(self, request: AssistantChatRequest) -> AssistantChatResponse:
            return AssistantChatResponse(reply_text="adapter", reply_audio_base64="audio", language=request.language)

    assistant_api.assistant_service = assistant_api.AssistantService(Adapter())
    response = client.post(
        "/assistant/chat",
        json={"message": "hello", "language": "hi", "input_type": "text", "audio_base64": None},
    )
    assert response.json() == {"reply_text": "adapter", "reply_audio_base64": "audio", "language": "hi"}


def test_vision_accepts_multipart_and_returns_exact_shape() -> None:
    response = client.post("/vision/diagnose", files={"image": ("leaf.jpg", b"image-bytes", "image/jpeg")})
    assert response.status_code == 200
    assert set(response.json()) == {"label", "confidence", "status", "recommendation", "nearby_inputs"}
    assert response.json()["status"] == "low_confidence_fallback"
    assert response.json()["confidence"] == 0
    assert set(response.json()["recommendation"]) == {
        "condition", "confidence", "what_to_do_now", "prevention", "treatment_options", "recommended_inputs", "sources",
    }


def test_vision_stub_is_deterministic_and_boundary_is_replaceable() -> None:
    first = client.post("/vision/diagnose", files={"image": ("a.jpg", b"a", "image/jpeg")})
    second = client.post("/vision/diagnose", files={"image": ("b.jpg", b"b", "image/jpeg")})
    assert first.json() == second.json()

    class Adapter:
        async def diagnose(self, image: bytes) -> VisionDiagnosis:
            return VisionDiagnosis.model_validate(first.json())

    vision_api.vision_service = vision_api.VisionService(Adapter())
    assert client.post("/vision/diagnose", files={"image": ("a.jpg", b"a", "image/jpeg")}).status_code == 200


def test_vision_requires_multipart_image() -> None:
    assert client.post("/vision/diagnose", json={}).status_code == 422
