from __future__ import annotations

from pathlib import Path

DOCUMENT_MAP = {
    "Apple___Cedar_apple_rust": "apple_cedar_apple_rust.md",
    "Apple___Black_rot": "apple_black_rot.md",
    "Apple___Apple_scab": "apple_apple_scab.md",
    "Tomato___Early_blight": "tomato_early_blight.md",
    "Tomato___Late_blight": "tomato_late_blight.md",
    "Tomato___Septoria_leaf_spot": "tomato_septoria_leaf_spot.md",
}


def retrieve_documents(disease_label: str, documents_dir: str | Path | None = None):
    """Return a matching disease document for a known PlantVillage label.

    If the label is unknown, return a clear 'not_found' payload.
    """
    if documents_dir is None:
        documents_dir = Path(__file__).resolve().parent / "documents"
    else:
        documents_dir = Path(documents_dir)

    filename = DOCUMENT_MAP.get(disease_label)
    if filename is None:
        return {
            "status": "not_found",
            "label": disease_label,
            "message": "No matching disease document exists for this label.",
        }

    document_path = documents_dir / filename
    if not document_path.exists():
        return {
            "status": "not_found",
            "label": disease_label,
            "message": f"Document file not found: {document_path.name}",
        }

    content = document_path.read_text(encoding="utf-8")
    return {
        "status": "found",
        "label": disease_label,
        "document": filename,
        "content": content,
        "path": str(document_path),
    }
