"""Tests for the pydantic validator adapter."""

from __future__ import annotations

from pydantic import BaseModel, Field

from vnvspec.validators.pydantic_adapter import pydantic_schema, validate_record


class Prediction(BaseModel):
    label: str
    score: float = Field(ge=0.0, le=1.0)


class TestPydanticSchema:
    def test_extracts_invariants(self) -> None:
        invariants = pydantic_schema(Prediction)
        names = {i.name for i in invariants}
        assert "label" in names
        assert "score" in names

    def test_invariant_count(self) -> None:
        invariants = pydantic_schema(Prediction)
        assert len(invariants) == 2


class TestValidateRecord:
    def test_valid_record_passes(self) -> None:
        ev = validate_record(Prediction, {"label": "cat", "score": 0.9})
        assert ev.verdict == "pass"
        assert ev.details["validator"] == "pydantic"

    def test_invalid_score_fails(self) -> None:
        ev = validate_record(Prediction, {"label": "cat", "score": 2.0})
        assert ev.verdict == "fail"
        assert "errors" in ev.details

    def test_missing_field_fails(self) -> None:
        ev = validate_record(Prediction, {"label": "cat"})
        assert ev.verdict == "fail"

    def test_wrong_type_fails(self) -> None:
        ev = validate_record(Prediction, {"label": 123, "score": 0.5})
        assert ev.verdict == "fail"

    def test_requirement_id_propagated(self) -> None:
        ev = validate_record(
            Prediction,
            {"label": "cat", "score": 0.5},
            requirement_id="REQ-001",
        )
        assert ev.requirement_id == "REQ-001"
