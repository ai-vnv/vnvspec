"""Tests for the Evidence model."""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from vnvspec.core.evidence import Evidence


class TestEvidence:
    def test_construction(self) -> None:
        e = Evidence(
            id="EV-001",
            requirement_id="REQ-001",
            kind="test",
            verdict="pass",
            artifact_uri="tests/results/run_001.json",
        )
        assert e.id == "EV-001"
        assert e.verdict == "pass"

    def test_auto_timestamp(self) -> None:
        e = Evidence(id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass")
        assert e.observed_at.tzinfo is not None

    def test_explicit_timestamp(self) -> None:
        ts = datetime(2026, 4, 1, 12, 0, 0, tzinfo=UTC)
        e = Evidence(
            id="EV-001",
            requirement_id="REQ-001",
            kind="analysis",
            verdict="fail",
            observed_at=ts,
        )
        assert e.observed_at == ts

    def test_invalid_kind(self) -> None:
        with pytest.raises(ValidationError):
            Evidence(
                id="EV-001",
                requirement_id="REQ-001",
                kind="magic",  # type: ignore[arg-type]
                verdict="pass",
            )

    def test_invalid_verdict(self) -> None:
        with pytest.raises(ValidationError):
            Evidence(
                id="EV-001",
                requirement_id="REQ-001",
                kind="test",
                verdict="maybe",  # type: ignore[arg-type]
            )

    def test_json_round_trip(self) -> None:
        e = Evidence(
            id="EV-001",
            requirement_id="REQ-001",
            kind="inspection",
            verdict="inconclusive",
            details={"inspector": "John", "notes": "Need more data"},
        )
        data = json.loads(e.model_dump_json())
        e2 = Evidence.model_validate(data)
        assert e.id == e2.id
        assert e.details == e2.details

    def test_all_verdicts(self) -> None:
        for verdict in ("pass", "fail", "inconclusive"):
            e = Evidence(
                id=f"EV-{verdict}",
                requirement_id="REQ-001",
                kind="test",
                verdict=verdict,  # type: ignore[arg-type]
            )
            assert e.verdict == verdict

    def test_all_kinds(self) -> None:
        for kind in ("test", "analysis", "inspection", "demonstration", "simulation"):
            e = Evidence(
                id=f"EV-{kind}",
                requirement_id="REQ-001",
                kind=kind,  # type: ignore[arg-type]
                verdict="pass",
            )
            assert e.kind == kind
