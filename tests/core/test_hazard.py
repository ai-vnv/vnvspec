"""Tests for the Hazard model."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from vnvspec.core.hazard import Hazard


class TestHazard:
    def test_construction(self) -> None:
        h = Hazard(
            id="HAZ-001",
            description="Incorrect object detection.",
            severity="S3",
            exposure="E4",
            controllability="C3",
            asil="D",
            mitigations=["REQ-001"],
        )
        assert h.id == "HAZ-001"
        assert h.asil == "D"
        assert h.mitigations == ["REQ-001"]

    def test_minimal(self) -> None:
        h = Hazard(
            id="HAZ-002",
            description="Sensor failure.",
            severity="S1",
            exposure="E1",
            controllability="C1",
            asil="QM",
        )
        assert h.mitigations == []

    def test_invalid_severity(self) -> None:
        with pytest.raises(ValidationError):
            Hazard(
                id="HAZ-001",
                description="Test.",
                severity="S5",  # type: ignore[arg-type]
                exposure="E1",
                controllability="C1",
                asil="QM",
            )

    def test_invalid_asil(self) -> None:
        with pytest.raises(ValidationError):
            Hazard(
                id="HAZ-001",
                description="Test.",
                severity="S1",
                exposure="E1",
                controllability="C1",
                asil="E",  # type: ignore[arg-type]
            )

    def test_json_round_trip(self) -> None:
        h = Hazard(
            id="HAZ-001",
            description="Test hazard.",
            severity="S2",
            exposure="E3",
            controllability="C2",
            asil="B",
            mitigations=["REQ-001", "REQ-002"],
            metadata={"source": "HARA workshop"},
        )
        data = json.loads(h.model_dump_json())
        h2 = Hazard.model_validate(data)
        assert h == h2
