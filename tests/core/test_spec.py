"""Tests for the Spec model."""

from __future__ import annotations

import json

import pytest

from vnvspec.core.errors import SpecError
from vnvspec.core.evidence import Evidence
from vnvspec.core.hazard import Hazard
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec


@pytest.fixture()
def sample_req() -> Requirement:
    return Requirement(
        id="REQ-001",
        statement="The system shall produce valid outputs.",
        rationale="Safety.",
        verification_method="test",
        acceptance_criteria=["All outputs valid."],
    )


@pytest.fixture()
def sample_hazard() -> Hazard:
    return Hazard(
        id="HAZ-001",
        description="Incorrect classification.",
        severity="S3",
        exposure="E4",
        controllability="C3",
        asil="D",
        mitigations=["REQ-001"],
    )


class TestSpecConstruction:
    def test_empty_spec(self) -> None:
        spec = Spec(name="empty")
        assert spec.name == "empty"
        assert len(spec.requirements) == 0

    def test_with_requirements(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        assert len(spec.requirements) == 1

    def test_duplicate_requirement_ids(self, sample_req: Requirement) -> None:
        with pytest.raises(SpecError, match="Duplicate requirement IDs"):
            Spec(name="bad", requirements=[sample_req, sample_req])

    def test_duplicate_hazard_ids(self, sample_hazard: Hazard) -> None:
        with pytest.raises(SpecError, match="Duplicate hazard IDs"):
            Spec(name="bad", hazards=[sample_hazard, sample_hazard])


class TestSpecLookup:
    def test_get_requirement(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        assert spec.get_requirement("REQ-001") == sample_req

    def test_get_requirement_not_found(self) -> None:
        spec = Spec(name="test")
        with pytest.raises(SpecError, match="not found"):
            spec.get_requirement("REQ-999")

    def test_get_hazard(self, sample_hazard: Hazard) -> None:
        spec = Spec(name="test", hazards=[sample_hazard])
        assert spec.get_hazard("HAZ-001") == sample_hazard

    def test_get_hazard_not_found(self) -> None:
        spec = Spec(name="test")
        with pytest.raises(SpecError, match="not found"):
            spec.get_hazard("HAZ-999")


class TestSpecEvidence:
    def test_evidence_for(self, sample_req: Requirement) -> None:
        ev = Evidence(id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass")
        spec = Spec(name="test", requirements=[sample_req], evidence=[ev])
        assert len(spec.evidence_for("REQ-001")) == 1
        assert len(spec.evidence_for("REQ-999")) == 0

    def test_coverage_summary_empty(self) -> None:
        spec = Spec(name="test")
        assert spec.coverage_summary() == {"total": 0, "covered": 0, "uncovered": 0}

    def test_coverage_summary_partial(self, sample_req: Requirement) -> None:
        req2 = Requirement(id="REQ-002", statement="Second.", verification_method="test")
        ev = Evidence(id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass")
        spec = Spec(name="test", requirements=[sample_req, req2], evidence=[ev])
        summary = spec.coverage_summary()
        assert summary == {"total": 2, "covered": 1, "uncovered": 1}


class TestSpecSerialization:
    def test_json_round_trip(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        data = json.loads(spec.model_dump_json())
        spec2 = Spec.model_validate(data)
        assert spec.name == spec2.name
        assert len(spec2.requirements) == 1
