from email import policy
from email.parser import BytesParser

from fastapi import APIRouter, HTTPException, Request

from app.schemas.vision import VisionDiagnosis
from app.services.vision_service import VisionService

router = APIRouter(prefix="/vision", tags=["vision"])
vision_service = VisionService()


def _image_from_multipart(content_type: str, body: bytes) -> bytes:
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(status_code=422, detail="image must be sent as multipart/form-data")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
    )
    for part in message.iter_parts():
        disposition = dict(part.get_params(header="content-disposition", unquote=True))
        if disposition.get("name") == "image":
            image = part.get_payload(decode=True)
            if image:
                return image
    raise HTTPException(status_code=422, detail="image field is required")


@router.post("/diagnose", response_model=VisionDiagnosis)
async def diagnose(request: Request) -> VisionDiagnosis:
    image = _image_from_multipart(request.headers.get("content-type", ""), await request.body())
    return await vision_service.diagnose(image)
