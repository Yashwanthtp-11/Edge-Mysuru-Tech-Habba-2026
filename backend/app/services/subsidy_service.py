import json
from collections.abc import Iterable
from pathlib import Path

from app.schemas.subsidy import Scheme, SubsidyContract


DEFAULT_DATA_PATH = Path(__file__).parents[2] / "data" / "subsidies.json"


def load_schemes(data_path: Path = DEFAULT_DATA_PATH) -> tuple[Scheme, ...]:
    try:
        payload = json.loads(data_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            return ()
        schemes = tuple(Scheme.model_validate(item) for item in payload)
        if len({scheme.id for scheme in schemes}) != len(schemes):
            return ()
        return schemes
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return ()


class SubsidyService:
    def __init__(self, schemes: Iterable[Scheme] | None = None, data_path: Path = DEFAULT_DATA_PATH) -> None:
        self.schemes = tuple(schemes) if schemes is not None else load_schemes(data_path)

    @staticmethod
    def _matches(scheme: Scheme, search: str | None) -> bool:
        if not search:
            return True
        term = search.casefold().strip()
        searchable = " ".join(
            value or ""
            for value in (scheme.name, scheme.description, scheme.category, scheme.state)
        )
        return term in searchable.casefold()

    def list_schemes(
        self,
        search: str | None = None,
        category: str | None = None,
        state: str | None = None,
        level: str | None = None,
        is_current: bool | None = None,
        limit: int = 20,
    ) -> list[Scheme]:
        filtered = [
            scheme
            for scheme in self.schemes
            if self._matches(scheme, search)
            and (category is None or scheme.category == category)
            and (state is None or (scheme.state and scheme.state.casefold() == state.casefold()))
            and (level is None or scheme.level == level)
            and (is_current is None or scheme.is_current is is_current)
        ]
        return sorted(filtered, key=lambda scheme: (scheme.name.casefold(), scheme.id))[:limit]

    def get_scheme(self, scheme_id: str) -> Scheme | None:
        return next((scheme for scheme in self.schemes if scheme.id == scheme_id), None)

    def list_contract_schemes(
        self,
        search: str | None = None,
        category: str | None = None,
        state: str | None = None,
        level: str | None = None,
        is_current: bool | None = None,
        limit: int = 20,
    ) -> list[SubsidyContract]:
        contracts = []
        for scheme in self.list_schemes(search, category, state, level, is_current, limit):
            if not scheme.verified:
                continue
            contracts.append(SubsidyContract(
                id=scheme.id,
                name=scheme.name,
                status=scheme.status,
                crop=scheme.crop,
                summary=scheme.summary,
            ))
        return contracts
