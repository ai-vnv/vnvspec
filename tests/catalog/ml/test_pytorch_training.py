"""Tests for the PyTorch training catalog.

Uses the catalog test fixture infrastructure from conftest.py to auto-validate
every requirement against the inclusion policy.
"""

from __future__ import annotations

import pytest

from vnvspec.catalog.ml.pytorch_training import (
    checkpointing,
    data_loading,
    gradient_health,
    loss_validation,
    reproducibility,
)
from vnvspec.core.requirement import Requirement

# Collect all catalog functions and their requirements for parametrized testing
_CATALOG_FUNCTIONS = [
    ("reproducibility", reproducibility),
    ("gradient_health", gradient_health),
    ("checkpointing", checkpointing),
    ("data_loading", data_loading),
    ("loss_validation", loss_validation),
]


def _all_requirements() -> list[tuple[str, Requirement]]:
    """Collect all requirements with their module name for parametrized tests."""
    results: list[tuple[str, Requirement]] = []
    for name, fn in _CATALOG_FUNCTIONS:
        for req in fn():
            results.append((name, req))
    return results


_ALL_REQS = _all_requirements()


class TestPyTorchTrainingCatalog:
    """Validate every PyTorch training catalog requirement."""

    def test_total_count(self) -> None:
        total = sum(len(fn()) for _, fn in _CATALOG_FUNCTIONS)
        assert total >= 30, f"Expected >= 30 requirements, got {total}"

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

    def test_all_ids_start_with_cat_pyt(self) -> None:
        for _, req in _ALL_REQS:
            assert req.id.startswith("CAT-PYT-"), f"{req.id} does not start with CAT-PYT-"

    def test_compatible_with_declared(self) -> None:
        import vnvspec.catalog.ml.pytorch_training as pkg

        assert hasattr(pkg, "__compatible_with__")
        assert "torch" in pkg.__compatible_with__

    def test_at_least_50_percent_have_standards(self) -> None:
        with_standards = sum(1 for _, req in _ALL_REQS if req.standards)
        pct = with_standards / len(_ALL_REQS)
        assert pct >= 0.5, f"Only {pct:.0%} have standards mappings (need >= 50%)"

    def test_module_docstring_has_scope_statement(self) -> None:
        import vnvspec.catalog.ml.pytorch_training as pkg

        assert pkg.__doc__ is not None
        assert "baseline, not a substitute for expert review" in pkg.__doc__

    @pytest.mark.parametrize("name,fn", _CATALOG_FUNCTIONS)
    def test_submodule_has_compat_pin(self, name: str, fn: object) -> None:
        import importlib

        mod = importlib.import_module(f"vnvspec.catalog.ml.pytorch_training.{name}")
        assert hasattr(mod, "__compatible_with__")


class TestReproducibility:
    def test_returns_requirements(self) -> None:
        reqs = reproducibility()
        assert isinstance(reqs, list)
        assert all(isinstance(r, Requirement) for r in reqs)
        assert len(reqs) >= 5

    def test_seed_requirement_is_blocking(self) -> None:
        reqs = reproducibility()
        seed_req = next(r for r in reqs if "REPRO-001" in r.id)
        assert seed_req.priority == "blocking"


class TestGradientHealth:
    def test_returns_requirements(self) -> None:
        reqs = gradient_health()
        assert len(reqs) >= 5


class TestCheckpointing:
    def test_returns_requirements(self) -> None:
        reqs = checkpointing()
        assert len(reqs) >= 5


class TestDataLoading:
    def test_returns_requirements(self) -> None:
        reqs = data_loading()
        assert len(reqs) >= 5


class TestLossValidation:
    def test_returns_requirements(self) -> None:
        reqs = loss_validation()
        assert len(reqs) >= 5
