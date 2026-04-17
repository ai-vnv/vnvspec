"""Tests for the JSON exporter."""

from __future__ import annotations

import json
from pathlib import Path

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.json_export import export_json


def _sample_report() -> Report:
    return Report(
        spec_name="test-spec",
        spec_version="1.0",
        evidence=[
            Evidence(id="EV-1", requirement_id="REQ-1", kind="test", verdict="pass"),
        ],
    )


def test_json_is_valid() -> None:
    text = export_json(_sample_report())
    data = json.loads(text)
    assert data["spec_name"] == "test-spec"


def test_json_contains_evidence() -> None:
    text = export_json(_sample_report())
    assert "EV-1" in text
    assert "REQ-1" in text


def test_json_write_to_file(tmp_path: Path) -> None:
    out = tmp_path / "report.json"
    result = export_json(_sample_report(), path=out)
    assert out.exists()
    assert out.read_text(encoding="utf-8") == result
