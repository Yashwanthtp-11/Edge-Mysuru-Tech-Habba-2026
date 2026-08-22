import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from ml.local_search.schemas import NearbyInputsSearchResult

load_dotenv()


def _distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math

    r = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


def _build_query(input_category: str) -> str:
    category = input_category.strip()
    if not category:
        raise ValueError("input_category is required")
    return category


def _parse_google_response(payload: Dict[str, Any], latitude: float, longitude: float) -> List[Dict[str, Any]]:
    places = payload.get("places") or []
    results: List[Dict[str, Any]] = []

    for place in places:
        location = place.get("location") or {}
        lat = location.get("latitude")
        lon = location.get("longitude")
        if lat is None or lon is None:
            continue

        distance_km = _distance_km(latitude, longitude, float(lat), float(lon))
        name = ((place.get("displayName") or {}).get("text") or "Unknown seller")
        address = place.get("formattedAddress") or "Address unavailable"
        maps_uri = place.get("googleMapsUri") or ""
        phone = (place.get("nationalPhoneNumber") or "") or None

        results.append(
            {
                "name": name,
                "address": address,
                "latitude": float(lat),
                "longitude": float(lon),
                "distance_km": round(distance_km, 2),
                "phone": phone,
                "website": None,
                "maps_uri": maps_uri,
                "stock_status": "not_verified",
            }
        )

    return results


def search_nearby_inputs(
    latitude: float,
    longitude: float,
    radius_km: float,
    input_category: str,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Search for nearby agricultural-input sellers via the Google Places API.

    If no API key is configured, return the same safe empty result format used elsewhere.
    """
    if not (-90 <= latitude <= 90):
        raise ValueError("latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise ValueError("longitude must be between -180 and 180")
    if radius_km <= 0:
        raise ValueError("radius_km must be positive")
    if not input_category or not input_category.strip():
        raise ValueError("input_category is required")

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return NearbyInputsSearchResult(status="provider_not_configured", results=[]).to_dict()

    query = _build_query(input_category)
    radius_meters = max(1, int(radius_km * 1000))
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.googleMapsUri,places.nationalPhoneNumber",
    }
    body = {
        "locationRestriction": {
            "circle": {
                "center": {"latitude": latitude, "longitude": longitude},
                "radius": radius_meters,
            }
        },
        "keyword": query,
        "maxResultCount": 5,
    }

    try:
        request = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return NearbyInputsSearchResult(status="provider_error", results=[]).to_dict()

    results = _parse_google_response(payload, latitude, longitude)
    return NearbyInputsSearchResult(status="ok", results=results).to_dict()
