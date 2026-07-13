"""Tests for the agentic AI governance catalog.

Uses the catalog test fixture infrastructure from conftest.py to auto-validate
every requirement against the inclusion policy.
"""

from __future__ import annotations

import re

import pytest

from vnvspec.catalog.ai.agentic_governance import tool_governance
from vnvspec.core.requirement import Requirement

# Collect all catalog functions and their requirements for parametrized testing.
_CATALOG_FUNCTIONS = [
    ("tool_governance", tool_governance),
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


class TestAgenticGovernanceCatalog:
    """Validate every agentic governance catalog requirement."""

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

    def test_all_ids_start_with_cat_agt(self) -> None:
        for _, req in _ALL_REQS:
            assert req.id.startswith("CAT-AGT-"), f"{req.id} does not start with CAT-AGT-"

    def test_at_least_50_percent_have_standards(self) -> None:
        with_standards = sum(1 for _, req in _ALL_REQS if req.standards)
        pct = with_standards / len(_ALL_REQS)
        assert pct >= 0.5, f"Only {pct:.0%} have standards mappings (need >= 50%)"

    def test_module_docstring_has_scope_statement(self) -> None:
        import importlib

        mod = importlib.import_module("vnvspec.catalog.ai.agentic_governance.tool_governance")
        assert mod.__doc__ is not None
        assert "baseline, not a substitute for expert review" in mod.__doc__

    def test_no_benchmark_metrics(self) -> None:
        for _, req in _ALL_REQS:
            for text in [req.statement, *req.acceptance_criteria]:
                assert not _BENCHMARK_RE.search(text), (
                    f"{req.id} contains a benchmark-style metric: {text!r}"
                )


class TestToolGovernance:
    def test_returns_requirements(self) -> None:
        reqs = tool_governance()
        assert isinstance(reqs, list)
        assert all(isinstance(r, Requirement) for r in reqs)
        assert len(reqs) >= 1

    def test_authorization_allowlist_is_blocking(self) -> None:
        reqs = tool_governance()
        allowlist = next(r for r in reqs if r.id == "CAT-AGT-TOOL-001")
        assert allowlist.priority == "blocking"
