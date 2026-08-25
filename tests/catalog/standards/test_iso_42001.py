"""Tests for the ISO/IEC 42001 catalog.

Uses the catalog test fixture infrastructure from conftest.py to auto-validate
every requirement against the inclusion policy.
"""

from __future__ import annotations

import pytest

from vnvspec import Spec
from vnvspec.catalog.standards.iso_42001 import annex_a_controls, management_controls
from vnvspec.core.requirement import Requirement
from vnvspec.core.trace import standard_gap_analysis

_CATALOG_FUNCTIONS = [
    ("management_controls", management_controls),
    ("annex_a_controls", annex_a_controls),
]


def _all_requirements() -> list[tuple[str, Requirement]]:
    """Collect all requirements with their module name for parametrized tests."""
    results: list[tuple[str, Requirement]] = []
    for name, fn in _CATALOG_FUNCTIONS:
        for req in fn():
            results.append((name, req))
    return results


_ALL_REQS = _all_requirements()


class TestISO42001Catalog:
    """Validate every ISO/IEC 42001 catalog requirement."""

    def test_total_count(self) -> None:
        total = sum(len(fn()) for _, fn in _CATALOG_FUNCTIONS)
        assert total >= 20, f"Expected >= 20 requirements, got {total}"

    @pytest.mark.parametrize("name,req", _ALL_REQS, ids=[r.id for _, r in _ALL_REQS])
    def test_requirement_validates(
        self,
        name: str,
        req: Requirement,
        catalog_validator: object,
    ) -> None:
        from tests.catalog.conftest import validate_catalog_requirement

        violations = validate_catalog_requirement(req)
        assert not violations, f"{req.id} failed validation:\n" + "\n".join(violations)

    def test_all_ids_unique(self) -> None:
        ids = [req.id for _, req in _ALL_REQS]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"

    def test_all_ids_start_with_cat_iso(self) -> None:
        for _, req in _ALL_REQS:
            assert req.id.startswith("CAT-ISO-"), f"{req.id} does not start with CAT-ISO-"

    def test_at_least_50_percent_have_standards(self) -> None:
        with_standards = sum(1 for _, req in _ALL_REQS if req.standards)
        pct = with_standards / len(_ALL_REQS)
        assert pct >= 0.5, f"Only {pct:.0%} have standards mappings (need >= 50%)"

    def test_module_docstring_has_scope_statement(self) -> None:
        import vnvspec.catalog.standards.iso_42001 as pkg

        assert pkg.__doc__ is not None
        assert "baseline, not a substitute for expert review" in pkg.__doc__

    def test_standard_gap_analysis_integration(self) -> None:
        """Verify that Spec composed of ISO 42001 requirements works with gap analysis."""
        reqs = [r for _, r in _ALL_REQS]
        spec = Spec(name="iso-42001-compliance-spec", requirements=reqs)
        gap_report = standard_gap_analysis(spec, "iso_42001")
        assert gap_report.covered > 0
        assert gap_report.total_clauses > 0
        assert len(gap_report.clauses) > 0

    def test_discovered_by_catalog_discovery(self) -> None:
        """Verify that discover_catalogs finds the ISO 42001 catalog."""
        from vnvspec.catalog._base import discover_catalogs

        catalogs = discover_catalogs()
        paths = [c.module_path for c in catalogs]
        assert any("standards.iso_42001" in p for p in paths)


class TestManagementControls:
    def test_returns_requirements(self) -> None:
        reqs = management_controls()
        assert isinstance(reqs, list)
        assert all(isinstance(r, Requirement) for r in reqs)
        assert len(reqs) >= 10


class TestAnnexAControls:
    def test_returns_requirements(self) -> None:
        reqs = annex_a_controls()
        assert isinstance(reqs, list)
        assert all(isinstance(r, Requirement) for r in reqs)
        assert len(reqs) >= 10
