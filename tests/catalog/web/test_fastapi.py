"""Tests for the FastAPI catalog."""

from __future__ import annotations

import pytest

from vnvspec.catalog.web.fastapi import api_design, observability, security_baseline
from vnvspec.core.requirement import Requirement

_CATALOG_FUNCTIONS = [
    ("security", security_baseline),
    ("observability", observability),
    ("api_design", api_design),
]


def _all_requirements() -> list[tuple[str, Requirement]]:
    results: list[tuple[str, Requirement]] = []
    for name, fn in _CATALOG_FUNCTIONS:
        for req in fn():
            results.append((name, req))
    return results


_ALL_REQS = _all_requirements()


class TestFastAPICatalog:
    def test_total_count(self) -> None:
        total = sum(len(fn()) for _, fn in _CATALOG_FUNCTIONS)
        assert total >= 22, f"Expected >= 22 requirements, got {total}"

    @pytest.mark.parametrize("name,req", _ALL_REQS, ids=[r.id for _, r in _ALL_REQS])
    def test_requirement_validates(self, name: str, req: Requirement) -> None:
        from tests.catalog.conftest import validate_catalog_requirement

        violations = validate_catalog_requirement(req)
        assert not violations, f"{req.id} failed:\n" + "\n".join(violations)

    def test_all_ids_unique(self) -> None:
        ids = [req.id for _, req in _ALL_REQS]
        assert len(ids) == len(set(ids))

    def test_all_ids_start_with_cat_fpi(self) -> None:
        for _, req in _ALL_REQS:
            assert req.id.startswith("CAT-FPI-"), f"{req.id} bad prefix"

    def test_owasp_api_2023_coverage(self) -> None:
        """All 10 OWASP API Security Top 10 2023 categories covered."""
        covered = set()
        for _, req in _ALL_REQS:
            for refs in req.standards.get("owasp_api_top10_2023", []):
                covered.add(refs)
        expected = {f"API{i}:2023" for i in range(1, 11)}
        missing = expected - covered
        assert not missing, f"Missing OWASP API 2023 categories: {missing}"

    def test_compatible_with_declared(self) -> None:
        import vnvspec.catalog.web.fastapi as pkg

        assert "fastapi" in pkg.__compatible_with__

    def test_module_docstring_has_scope_statement(self) -> None:
        import vnvspec.catalog.web.fastapi as pkg

        assert pkg.__doc__ is not None
        assert "baseline, not a substitute for expert review" in pkg.__doc__

    @pytest.mark.parametrize("name,fn", _CATALOG_FUNCTIONS)
    def test_submodule_has_compat_pin(self, name: str, fn: object) -> None:
        import importlib

        mod = importlib.import_module(
            f"vnvspec.catalog.web.fastapi.{name if name != 'security' else 'security'}"
        )
        assert hasattr(mod, "__compatible_with__")
