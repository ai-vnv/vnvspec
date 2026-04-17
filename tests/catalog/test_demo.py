"""Tests for the demo catalog module."""

from __future__ import annotations

from vnvspec.catalog.demo import hello_world
from vnvspec.core.requirement import Requirement


class TestDemoCatalog:
    def test_import(self) -> None:
        reqs = hello_world()
        assert isinstance(reqs, list)
        assert len(reqs) == 1

    def test_requirement_type(self) -> None:
        reqs = hello_world()
        assert isinstance(reqs[0], Requirement)

    def test_requirement_id(self) -> None:
        reqs = hello_world()
        assert reqs[0].id == "CAT-DEMO-001"

    def test_requirement_fields(self) -> None:
        req = hello_world()[0]
        assert "deterministic" in req.statement
        assert req.verification_method == "test"
        assert len(req.acceptance_criteria) == 1
        assert req.rationale != ""
        assert len(req.source) > 0
