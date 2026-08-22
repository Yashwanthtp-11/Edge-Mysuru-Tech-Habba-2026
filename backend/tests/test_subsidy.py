from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.api import subsidy as subsidy_api
from app.main import app
from app.schemas.subsidy import Scheme
from app.services.subsidy_service import SubsidyService

client = TestClient(app)


SCHEMES = [
    Scheme(
        id="karnataka-drip",
        name="Karnataka Drip Support",
        level="state",
        state="Karnataka",
        category="irrigation",
        description="Official irrigation scheme record.",
        official_source="https://karnataka.gov.in/",
        last_verified=datetime(2026, 8, 22, tzinfo=timezone.utc),
        is_current=True,
    ),
    Scheme(
        id="pm-kisan",
        name="PM-KISAN",
        level="central",
        category="income support",
        description="Official central scheme record.",
        official_source="https://pmkisan.gov.in/",
        application_url="https://pmkisan.gov.in/",
        is_current=True,
    ),
    Scheme(
        id="old-insurance",
        name="Historical Crop Record",
        level="central",
        state="Karnataka",
        category="insurance",
        is_current=False,
    ),
]


def use_test_service(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subsidy_api, "subsidy_service", SubsidyService(SCHEMES))


def test_list_endpoint_returns_normalized_records(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/list")
    assert response.status_code == 200
    assert response.json() == {"subsidies": []}
    assert [item.name for item in subsidy_api.subsidy_service.list_schemes()] == [
        "Historical Crop Record", "Karnataka Drip Support", "PM-KISAN"
    ]


def test_detail_endpoint_preserves_official_information(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/pm-kisan")
    assert response.status_code == 200
    assert response.json()["official_source"] == "https://pmkisan.gov.in/"
    assert response.json()["application_url"] == "https://pmkisan.gov.in/"


def test_unknown_scheme_returns_404(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/unknown")
    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SCHEME_NOT_FOUND"


def test_search_filtering(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/list?search=irrigation")
    assert response.json() == {"subsidies": []}
    assert [item.id for item in subsidy_api.subsidy_service.list_schemes(search="irrigation")] == ["karnataka-drip"]


def test_category_filtering(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/list?category=insurance")
    assert response.json() == {"subsidies": []}
    assert [item.id for item in subsidy_api.subsidy_service.list_schemes(category="insurance")] == ["old-insurance"]


def test_state_filtering(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/list?state=kArNaTaKa")
    assert response.json() == {"subsidies": []}
    assert [item.id for item in subsidy_api.subsidy_service.list_schemes(state="kArNaTaKa")] == ["old-insurance", "karnataka-drip"]


def test_current_status_filtering(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/list?is_current=false")
    assert response.json() == {"subsidies": []}
    assert [item.id for item in subsidy_api.subsidy_service.list_schemes(is_current=False)] == ["old-insurance"]


def test_ordering_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    first = [item.id for item in subsidy_api.subsidy_service.list_schemes()]
    second = [item.id for item in subsidy_api.subsidy_service.list_schemes()]
    assert first == second


def test_missing_fields_remain_unverified(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    scheme = client.get("/subsidy/old-insurance").json()
    assert scheme["benefit"] is None
    assert scheme["eligibility"] is None
    assert scheme["documents"] is None
    assert scheme["official_source"] is None
    assert scheme["is_current"] is False


def test_no_fabricated_benefit_values_in_default_catalog() -> None:
    response = client.get("/subsidy/list")
    assert response.status_code == 200
    assert response.json() == {"subsidies": []}


def test_invalid_limit_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    assert client.get("/subsidy/list?limit=0").status_code == 422
    assert client.get("/subsidy/list?limit=101").status_code == 422


def test_empty_result_is_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    use_test_service(monkeypatch)
    response = client.get("/subsidy/list?search=does-not-exist")
    assert response.status_code == 200
    assert response.json() == {"subsidies": []}


def test_default_catalog_contains_requested_names(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subsidy_api, "subsidy_service", SubsidyService())
    names = {item.name for item in subsidy_api.subsidy_service.list_schemes()}
    assert {"PM-KISAN", "PMFBY", "Kisan Credit Card", "PM-KUSUM"}.issubset(names)


def test_verified_contract_metadata_is_adapted_without_extra_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    verified = Scheme(
        id="verified-example",
        name="Verified Example",
        status="ongoing",
        crop="tomato",
        summary="Verified record.",
    )
    monkeypatch.setattr(subsidy_api, "subsidy_service", SubsidyService([verified]))
    response = client.get("/subsidy/list")
    assert response.status_code == 200
    assert response.json() == {
        "subsidies": [{
            "id": "verified-example",
            "name": "Verified Example",
            "status": "ongoing",
            "crop": "tomato",
            "summary": "Verified record.",
        }]
    }
