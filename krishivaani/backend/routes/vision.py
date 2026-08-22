import os
import sys
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from ml.diagnose import diagnose_and_recommend


router = APIRouter(prefix="/vision", tags=["Vision"])


@router.post("/diagnose")
async def diagnose(
	image: Optional[UploadFile] = File(None),
	latitude: Optional[float] = Form(None),
	longitude: Optional[float] = Form(None),
	radius_km: float = Form(10),
):
	if image is None or not image.filename:
		raise HTTPException(status_code=400, detail="An image file is required.")
	if image.content_type and not image.content_type.startswith("image/"):
		raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

	suffix = Path(image.filename).suffix or ".img"
	temporary_path = None
	try:
		with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
			temporary_path = temporary_file.name
			content = await image.read()
			if not content:
				raise HTTPException(status_code=400, detail="Uploaded image is empty.")
			temporary_file.write(content)

		return diagnose_and_recommend(
			temporary_path,
			latitude=latitude,
			longitude=longitude,
			radius_km=radius_km,
		)
	finally:
		if temporary_path and os.path.exists(temporary_path):
			os.remove(temporary_path)
