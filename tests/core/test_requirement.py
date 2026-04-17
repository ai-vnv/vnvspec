"""Tests for the Requirement model."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from vnvspec.core.requirement import Requirement


class TestRequirementConstruction:
    def test_minimal_construction(self) -> None:
        req = Requirement(id="REQ-001", statement="The system shall work.")
        assert req.id == "REQ-001"
        assert req.statement == "The system shall work."
        assert req.verification_method == "test"
        assert req.priority == "medium"

    def test_full_construction(self) -> None:
        req = Requirement(
            id="REQ-002",
            statement="The system shall respond within 100 ms.",
            rationale="Latency budget.",
            source="Architecture doc §3.2",
            priority="high",
            verification_method="analysis",
            standards={"iso_pas_8800": ["6.2.1"]},
            ontology_refs=["driving:speed"],
            acceptance_criteria=["p99 < 100 ms"],
            metadata={"author": "test"},
        )
        assert req.priority == "high"
        assert req.standards == {"iso_pas_8800": ["6.2.1"]}
        assert req.ontology_refs == ["driving:speed"]
        assert len(req.acceptance_criteria) == 1

    def test_frozen(self) -> None:
        req = Requirement(id="REQ-001", statement="Test.")
        with pytest.raises(ValidationError):
            req.id = "REQ-002"  # type: ignore[misc]

    def test_invalid_verification_method(self) -> None:
        with pytest.raises(ValidationError):
            Requirement(id="REQ-001", statement="Test.", verification_method="magic")  # type: ignore[arg-type]

    def test_invalid_priority(self) -> None:
        with pytest.raises(ValidationError):
            Requirement(id="REQ-001", statement="Test.", priority="critical")  # type: ignore[arg-type]


class TestRequirementSerialization:
    def test_json_round_trip(self) -> None:
        req = Requirement(
            id="REQ-001",
            statement="The system shall classify images.",
            rationale="Core function.",
            verification_method="test",
            acceptance_criteria=["Accuracy > 0.9"],
        )
        data = json.loads(req.model_dump_json())
        req2 = Requirement.model_validate(data)
        assert req == req2

    def test_dict_round_trip(self) -> None:
        req = Requirement(id="REQ-001", statement="Test.", rationale="Reason.")
        d = req.model_dump()
        req2 = Requirement.model_validate(d)
        assert req == req2


class TestFormalProof:
    def test_formal_proof_is_valid_verification_method(self) -> None:
        req = Requirement(
            id="REQ-FP-001",
            statement="The model shall be robust to L-inf perturbations.",
            verification_method="formal_proof",
        )
        assert req.verification_method == "formal_proof"

    def test_formal_proof_round_trips(self) -> None:
        req = Requirement(
            id="REQ-FP-001",
            statement="Test.",
            verification_method="formal_proof",
        )
        data = json.loads(req.model_dump_json())
        req2 = Requirement.model_validate(data)
        assert req2.verification_method == "formal_proof"
