from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SellerResult:
    name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    phone: Optional[str] = None
    website: Optional[str] = None
    maps_uri: Optional[str] = None
    stock_status: str = "not_verified"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class NearbyInputsSearchResult:
    status: str
    results: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {"status": self.status, "results": self.results}
