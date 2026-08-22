import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch
from transformers import pipeline

from ml.rag.retrieve import retrieve_documents

MODEL_NAME = "kimcomehome/plantvillage-vit-leaf-disease"
CONFIDENCE_THRESHOLD = 0.70


def analyze_image(image_path: str):
    image_file = Path(image_path).expanduser()
    if not image_file.exists():
        return {
            "status": "error",
            "message": f"Image does not exist: {image_file}",
        }

    if not image_file.is_file():
        return {
            "status": "error",
            "message": f"Path is not a file: {image_file}",
        }

    if torch.cuda.is_available():
        device = 0
    else:
        device = -1

    classifier = pipeline("image-classification", model=MODEL_NAME, device=device)
    result = classifier(str(image_file))
    top_prediction = result[0]
    predicted_label = top_prediction["label"]
    confidence = float(top_prediction["score"])

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "status": "uncertain",
            "predicted_label": predicted_label,
            "confidence": confidence,
            "message": "The image confidence is too low for a disease-specific recommendation. Please provide a clearer image.",
            "retrieval_status": "skipped",
        }

    retrieval = retrieve_documents(predicted_label)
    if retrieval["status"] == "found":
        return {
            "status": "possible_diagnosis",
            "predicted_label": predicted_label,
            "confidence": confidence,
            "retrieval_status": "found",
            "document": retrieval["document"],
            "document_text": retrieval["content"],
        }

    return {
        "status": "knowledge_not_found",
        "predicted_label": predicted_label,
        "confidence": confidence,
        "retrieval_status": "not_found",
        "message": "The model predicted a condition, but no trusted disease guidance exists for it in the local knowledge base.",
    }


def main():
    if len(sys.argv) != 2:
        print(json.dumps({"status": "error", "message": "Usage: python analyze.py <image-path>"}))
        raise SystemExit(1)

    result = analyze_image(sys.argv[1])
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
