import json
import re
from typing import Any, Dict, List, Optional

from ml.local_search.nearby_inputs import search_nearby_inputs


def build_uncertain_response(confidence: float, message: str = "I cannot reliably identify the plant problem from this image. Please provide a clearer image.") -> Dict[str, Any]:
    return {
        "status": "uncertain",
        "confidence": confidence,
        "message": message,
        "nearby_sellers": [],
    }


def parse_crop_and_condition(predicted_label: str) -> Dict[str, str]:
    if "___" not in predicted_label:
        return {"crop": "Unknown", "condition": predicted_label}

    crop, condition = predicted_label.split("___", 1)
    return {
        "crop": crop.replace("_", " "),
        "condition": condition.replace("_", " "),
    }


def _extract_section(document_text: str, heading: str) -> List[str]:
    captures: List[str] = []
    in_section = False

    for raw_line in document_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("## "):
            section_name = line[3:].strip().lower()
            in_section = section_name == heading.lower()
            continue

        if in_section:
            if line.startswith("-"):
                captures.append(line[1:].strip())
            elif line.startswith("#"):
                continue
            else:
                captures.append(line)

    return captures


def _extract_sources(document_text: str) -> List[str]:
    matches = re.findall(r"https?://[^\s)]+", document_text)
    return matches


def _build_recommended_inputs(document_text: str) -> List[Dict[str, str]]:
    lower = document_text.lower()
    recommendations: List[Dict[str, str]] = []

    if "fungicide" in lower:
        recommendations.append({
            "category": "fungicide",
            "purpose": "Disease management",
            "stock_status": "not_verified",
        })

    if "resistant" in lower:
        recommendations.append({
            "category": "resistant planting material",
            "purpose": "Reduce infection pressure",
            "stock_status": "not_verified",
        })

    if "crop rotation" in lower or "rotate crops" in lower:
        recommendations.append({
            "category": "crop rotation planning",
            "purpose": "Lower disease carryover and improve field sanitation",
            "stock_status": "not_verified",
        })

    if not recommendations:
        recommendations.append({
            "category": "local extension guidance",
            "purpose": "Follow current local label guidance for disease management",
            "stock_status": "not_verified",
        })

    return recommendations


def _search_recommended_inputs(
    recommended_inputs: List[Dict[str, str]],
    latitude: Optional[float],
    longitude: Optional[float],
    radius_km: float,
) -> Dict[str, Any]:
    if latitude is None or longitude is None:
        return {"location_status": "not_provided", "nearby_sellers": []}

    nearby_sellers: List[Dict[str, Any]] = []
    provider_statuses: List[str] = []
    for recommended_input in recommended_inputs:
        try:
            search_result = search_nearby_inputs(
                latitude,
                longitude,
                radius_km,
                recommended_input["category"],
                provider="google",
            )
        except (TypeError, ValueError):
            provider_statuses.append("provider_error")
            continue

        provider_statuses.append(search_result.get("status", "provider_error"))
        nearby_sellers.extend(search_result.get("results", []))

    if "provider_error" in provider_statuses:
        location_status = "provider_error"
    elif "ok" in provider_statuses:
        location_status = "ok"
    else:
        location_status = provider_statuses[0] if provider_statuses else "provider_error"

    return {
        "location_status": location_status,
        "nearby_sellers": nearby_sellers,
    }


def build_recommendation(
    vision_result: Dict[str, Any],
    retrieved_document: Dict[str, Any] | None = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    radius_km: float = 10,
):
    """Build a JSON-serializable recommendation result from a valid, high-confidence diagnosis."""
    if not isinstance(vision_result, dict):
        raise ValueError("vision_result must be a dictionary")

    status = vision_result.get("status")
    if status == "uncertain":
        return build_uncertain_response(
            confidence=float(vision_result.get("confidence", 0.0)),
            message=vision_result.get(
                "message",
                "I cannot reliably identify the plant problem from this image. Please provide a clearer image.",
            ),
        )

    predicted_label = vision_result.get("predicted_label")
    confidence = float(vision_result.get("confidence", 0.0))
    crop_condition = parse_crop_and_condition(predicted_label or "Unknown")

    document_text = ""
    sources: List[str] = []
    if isinstance(retrieved_document, dict) and retrieved_document.get("status") == "found":
        document_text = retrieved_document.get("content", "")
        sources = _extract_sources(document_text)

    what_to_do_now = _extract_section(document_text, "Management")
    prevention = _extract_section(document_text, "Prevention")
    treatment_options = _extract_section(document_text, "Management")
    recommended_inputs = _build_recommended_inputs(document_text)

    if not what_to_do_now:
        what_to_do_now = ["Follow the local extension guidance in the retrieved disease document."]
    if not prevention:
        prevention = ["Use the prevention guidance in the retrieved disease document and monitor field conditions."]
    if not treatment_options:
        treatment_options = ["Use current local extension guidance and product labels for disease management."]
    if not sources:
        sources = ["Retrieved disease document"]

    local_search = _search_recommended_inputs(
        recommended_inputs,
        latitude,
        longitude,
        radius_km,
    )

    recommendation = {
        "status": "grounded",
        "crop": crop_condition["crop"],
        "condition": crop_condition["condition"],
        "confidence": confidence,
        "what_to_do_now": what_to_do_now,
        "prevention": prevention,
        "treatment_options": treatment_options,
        "recommended_inputs": recommended_inputs,
        "sources": sources,
        "location_status": local_search["location_status"],
        "nearby_sellers": local_search["nearby_sellers"],
    }
    return recommendation


def main():
    example = {
        "status": "possible_diagnosis",
        "predicted_label": "Apple___Cedar_apple_rust",
        "confidence": 0.851235,
    }
    print(json.dumps(build_recommendation(example), indent=2))


if __name__ == "__main__":
    main()
