from collections.abc import Iterable

from app.schemas.subsidy import Scheme


DEFAULT_SCHEMES = (
    Scheme(id="pm-kisan", name="PM-KISAN"),
    Scheme(id="pmfby", name="PMFBY"),
    Scheme(id="kisan-credit-card", name="Kisan Credit Card"),
    Scheme(id="pmksy-per-drop-more-crop", name="PMKSY - Per Drop More Crop"),
    Scheme(id="pm-kusum", name="PM-KUSUM"),
    Scheme(id="soil-health-card", name="Soil Health Card"),
)


class SubsidyService:
    def __init__(self, schemes: Iterable[Scheme] | None = None) -> None:
        self.schemes = tuple(schemes if schemes is not None else DEFAULT_SCHEMES)

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
