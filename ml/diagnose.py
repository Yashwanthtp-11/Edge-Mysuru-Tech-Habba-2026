import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml.rag.retrieve import retrieve_documents
from ml.recommendation.build_recommendation import build_recommendation
from ml.vision.analyze import analyze_image


def diagnose_and_recommend(
    image_path: str,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 10,
) -> Dict[str, Any]:
    """Run vision, trusted-document retrieval, and recommendation generation."""
    vision_result = analyze_image(image_path)
    if vision_result.get("status") == "uncertain":
        return build_recommendation(vision_result)

    predicted_label = vision_result.get("predicted_label")
    if not predicted_label:
        return build_recommendation(vision_result)

    retrieved_document = None
    if vision_result.get("retrieval_status") == "found":
        retrieved_document = retrieve_documents(predicted_label)

    return build_recommendation(
        vision_result,
        retrieved_document,
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose a plant image and build a recommendation.")
    parser.add_argument("image_path")
    parser.add_argument("--latitude", type=float)
    parser.add_argument("--longitude", type=float)
    parser.add_argument("--radius-km", type=float, default=10)
    args = parser.parse_args()

    result = diagnose_and_recommend(
        args.image_path,
        latitude=args.latitude,
        longitude=args.longitude,
        radius_km=args.radius_km,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
