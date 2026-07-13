"""Tests for the Human Oversight catalog.

Uses the catalog test fixture infrastructure from conftest.py to auto-validate
every requirement against the inclusion policy.
"""

from __future__ import annotations

import re

import pytest

from vnvspec.catalog.ai.agentic_governance import human_oversight
from vnvspec.core.requirement import Requirement

# Collect all catalog functions and their requirements for parametrized testing.
_CATALOG_FUNCTIONS = [
    ("human_oversight", human_oversight),
]


def _all_requirements() -> list[tuple[str, Requirement]]:
    """Collect all requirements with their module name for parametrized tests."""
    results: list[tuple[str, Requirement]] = []
    for name, fn in _CATALOG_FUNCTIONS:
        for req in fn():
            results.append((name, req))
    return results


_ALL_REQS = _all_requirements()

# Matches benchmark-style metrics such as "95%", "95 percent", or "0.95 rate".
_BENCHMARK_RE = re.compile(r"\d+\s*%|\b\d+(?:\.\d+)?\s*(?:percent|rate)\b", re.IGNORECASE)


class TestHumanOversightCatalog:
    """Validate every human oversight catalog requirement."""

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

    def test_all_ids_start_with_cat_agt_hum(self) -> None:
        for _, req in _ALL_REQS:
            assert req.id.startswith("CAT-AGT-HUM-"), f"{req.id} does not start with CAT-AGT-HUM-"

    def test_at_least_50_percent_have_standards(self) -> None:
        with_standards = sum(1 for _, req in _ALL_REQS if req.standards)
        pct = with_standards / len(_ALL_REQS)
        assert pct >= 0.5, f"Only {pct:.0%} have standards mappings (need >= 50%)"

    def test_module_docstring_has_scope_statement(self) -> None:
        import importlib

        mod = importlib.import_module("vnvspec.catalog.ai.agentic_governance.human_oversight")
        assert mod.__doc__ is not None
        assert "baseline, not a substitute for expert review" in mod.__doc__

    def test_no_benchmark_metrics(self) -> None:
        for _, req in _ALL_REQS:
            for text in [req.statement, *req.acceptance_criteria]:
                assert not _BENCHMARK_RE.search(text), (
                    f"{req.id} contains a benchmark-style metric: {text!r}"
                )


class TestHumanOversight:
    def test_returns_requirements(self) -> None:
        reqs = human_oversight()
        assert isinstance(reqs, list)
        assert all(isinstance(r, Requirement) for r in reqs)
        assert reqs  # non-empty; no fixed total count asserted

    def test_high_impact_approval_is_blocking(self) -> None:
        reqs = human_oversight()
        req = next(r for r in reqs if r.id == "CAT-AGT-HUM-001")
        assert req.priority == "blocking"

    def test_halt_capability_is_blocking(self) -> None:
        reqs = human_oversight()
        req = next(r for r in reqs if r.id == "CAT-AGT-HUM-006")
        assert req.priority == "blocking"

    def test_oversight_integrity_is_blocking(self) -> None:
        reqs = human_oversight()
        req = next(r for r in reqs if r.id == "CAT-AGT-HUM-007")
        assert req.priority == "blocking"

    def test_intervention_accountability_present(self) -> None:
        reqs = human_oversight()
        ids = {r.id for r in reqs}
        assert "CAT-AGT-HUM-008" in ids
