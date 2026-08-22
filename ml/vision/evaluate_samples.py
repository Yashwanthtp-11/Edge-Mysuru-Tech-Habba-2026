import csv
import sys
from pathlib import Path

import torch
from transformers import pipeline

MODEL_NAME = "kimcomehome/plantvillage-vit-leaf-disease"
REQUIRED_COLUMNS = {"image", "label", "source"}


def load_manifest(manifest_path: Path):
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    with manifest_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)

        if reader.fieldnames is None:
            raise ValueError(f"Manifest is empty or missing a header: {manifest_path}")

        missing = REQUIRED_COLUMNS - set(reader.fieldnames)
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise ValueError(f"Manifest is missing required columns: {missing_str}")

        rows = list(reader)
        if not rows:
            raise ValueError(f"Manifest is empty: {manifest_path}")

    return rows


def resolve_image_path(project_root: Path, image_value: str) -> Path:
    image_path = Path(image_value)
    if image_path.is_absolute():
        resolved = image_path
    else:
        resolved = project_root / image_path

    if not resolved.exists():
        raise FileNotFoundError(f"Image not found: {resolved}")

    if not resolved.is_file():
        raise ValueError(f"Image path is not a file: {resolved}")

    return resolved


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(sys.argv[0]).name} <manifest.csv>")
        raise SystemExit(1)

    manifest_path = Path(sys.argv[1]).expanduser()
    project_root = Path(__file__).resolve().parents[2]

    if not manifest_path.is_absolute():
        manifest_path = project_root / manifest_path

    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    try:
        rows = load_manifest(manifest_path)
    except Exception as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    if torch.cuda.is_available():
        device = 0
        print(f"Using CUDA: {torch.cuda.get_device_name(0)}")
    else:
        device = -1
        print("CUDA not available. Using CPU.")

    print(f"Loading model: {MODEL_NAME}")
    classifier = pipeline("image-classification", model=MODEL_NAME, device=device)
    print("Model loaded successfully.")

    total = 0
    correct = 0
    total_confidence = 0.0

    print("\nEvaluating samples:")
    for index, row in enumerate(rows, start=1):
        image_value = row.get("image", "").strip()
        expected_label = row.get("label", "").strip()
        source = row.get("source", "").strip()

        if not image_value or not expected_label or not source:
            raise ValueError(f"Row {index} is missing required data: {row}")

        image_path = resolve_image_path(project_root, image_value)
        result = classifier(str(image_path))
        top_prediction = result[0]
        predicted_label = top_prediction["label"]
        confidence = float(top_prediction["score"])

        is_correct = predicted_label == expected_label
        if is_correct:
            correct += 1
        total += 1
        total_confidence += confidence

        print(
            f"{index}. expected={expected_label} | predicted={predicted_label} | "
            f"confidence={confidence:.6f} | correct={is_correct} | source={source}"
        )

    if total == 0:
        raise ValueError("No rows were processed from the manifest.")

    accuracy = correct / total
    avg_confidence = total_confidence / total

    print("\nSummary:")
    print(f"Total images: {total}")
    print(f"Correct: {correct}")
    print(f"Incorrect: {total - correct}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Average top-1 confidence: {avg_confidence:.6f}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
