from typing import Any, Dict, Optional

from ml.local_search.schemas import NearbyInputsSearchResult


def search_nearby_inputs(
    latitude: float,
    longitude: float,
    radius_km: float,
    input_category: str,
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """Return a safe, provider-independent nearby-seller search result.

    Without a configured provider, we return a clean empty result and do not invent seller data.
    """
    if radius_km <= 0:
        raise ValueError("radius_km must be positive")
    if not input_category or not input_category.strip():
        raise ValueError("input_category is required")

    if provider is None:
        return NearbyInputsSearchResult(status="provider_not_configured", results=[]).to_dict()

    return NearbyInputsSearchResult(status="provider_not_configured", results=[]).to_dict()
