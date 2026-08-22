import sys
from pathlib import Path

import torch
from transformers import pipeline

MODEL_NAME = "kimcomehome/plantvillage-vit-leaf-disease"


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(sys.argv[0]).name} \"<image-path>\"")
        raise SystemExit(1)

    image_path = Path(sys.argv[1]).expanduser()

    if not image_path.exists():
        print(f"Error: image does not exist: {image_path}")
        raise SystemExit(1)

    if not image_path.is_file():
        print(f"Error: path is not a file: {image_path}")
        raise SystemExit(1)

    if torch.cuda.is_available():
        device = 0
        device_name = torch.cuda.get_device_name(0)
        print(f"Using CUDA: {device_name}")
    else:
        device = -1
        print("CUDA not available. Using CPU.")

    print(f"Loading model: {MODEL_NAME}")

    classifier = pipeline(
        "image-classification",
        model=MODEL_NAME,
        device=device,
    )

    print("Model loaded successfully.")
    print(f"Running inference on: {image_path}")

    outputs = classifier(str(image_path))
    print("Top 5 predictions:")
    for i, item in enumerate(outputs[:5], start=1):
        label = item["label"]
        score = item["score"]
        print(f"{i}. {label} - {score:.6f}")


if __name__ == "__main__":
    main()
