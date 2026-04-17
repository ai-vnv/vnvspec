"""Tests for the Pyomo catalog."""

from __future__ import annotations

import pytest

from vnvspec.catalog.optimization.pyomo import (
    constraint_validation,
    model_invariants,
    solver_status,
)
from vnvspec.core.requirement import Requirement

_CATALOG_FUNCTIONS = [
    ("solver_status", solver_status),
    ("constraint_validation", constraint_validation),
    ("model_invariants", model_invariants),
]


def _all_requirements() -> list[tuple[str, Requirement]]:
    results: list[tuple[str, Requirement]] = []
    for name, fn in _CATALOG_FUNCTIONS:
        for req in fn():
            results.append((name, req))
    return results


_ALL_REQS = _all_requirements()


class TestPyomoCatalog:
    def test_total_count(self) -> None:
        total = sum(len(fn()) for _, fn in _CATALOG_FUNCTIONS)
        assert total >= 18, f"Expected >= 18 requirements, got {total}"

    @pytest.mark.parametrize("name,req", _ALL_REQS, ids=[r.id for _, r in _ALL_REQS])
    def test_requirement_validates(self, name: str, req: Requirement) -> None:
        from tests.catalog.conftest import validate_catalog_requirement

        violations = validate_catalog_requirement(req)
        assert not violations, f"{req.id} failed:\n" + "\n".join(violations)

    def test_all_ids_unique(self) -> None:
        ids = [req.id for _, req in _ALL_REQS]
        assert len(ids) == len(set(ids))

    def test_all_ids_start_with_cat_pyo(self) -> None:
        for _, req in _ALL_REQS:
            assert req.id.startswith("CAT-PYO-"), f"{req.id} bad prefix"

    def test_compatible_with_declared(self) -> None:
        import vnvspec.catalog.optimization.pyomo as pkg

        assert "pyomo" in pkg.__compatible_with__

    def test_module_docstring_has_scope_statement(self) -> None:
        import vnvspec.catalog.optimization.pyomo as pkg

        assert pkg.__doc__ is not None
        assert "baseline, not a substitute for expert review" in pkg.__doc__
