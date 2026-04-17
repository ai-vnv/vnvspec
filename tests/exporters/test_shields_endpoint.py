"""Tests for the Shields.io endpoint exporter."""

from __future__ import annotations

import json
from pathlib import Path

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.shields_endpoint import export_shields_endpoint


class TestShieldsEndpoint:
    def test_all_pass(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
                Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="pass"),
            ],
        )
        path = tmp_path / "badge.json"
        result = export_shields_endpoint(report, path=path)
        assert result == path
        data = json.loads(path.read_text())
        assert data["schemaVersion"] == 1
        assert data["label"] == "V&V"
        assert data["color"] == "green"
        assert "2/2" in data["message"]
        assert "pass" in data["message"]

    def test_any_fail(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
                Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="fail"),
            ],
        )
        path = tmp_path / "badge.json"
        export_shields_endpoint(report, path=path)
        data = json.loads(path.read_text())
        assert data["color"] == "red"
        assert "failed" in data["message"]

    def test_inconclusive(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
                Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="inconclusive"),
            ],
        )
        path = tmp_path / "badge.json"
        export_shields_endpoint(report, path=path)
        data = json.loads(path.read_text())
        assert data["color"] == "yellow"
        assert "inconclusive" in data["message"]

    def test_no_evidence(self, tmp_path: Path) -> None:
        report = Report(spec_name="test")
        path = tmp_path / "badge.json"
        export_shields_endpoint(report, path=path)
        data = json.loads(path.read_text())
        assert data["color"] == "lightgrey"
        assert "no evidence" in data["message"]

    def test_custom_label(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
            ],
        )
        path = tmp_path / "badge.json"
        export_shields_endpoint(report, path=path, label="Safety V&V")
        data = json.loads(path.read_text())
        assert data["label"] == "Safety V&V"

    def test_valid_json_structure(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
            ],
        )
        path = tmp_path / "badge.json"
        export_shields_endpoint(report, path=path)
        data = json.loads(path.read_text())
        assert set(data.keys()) == {"schemaVersion", "label", "message", "color"}
        assert isinstance(data["schemaVersion"], int)
        assert isinstance(data["label"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["color"], str)

    def test_fail_takes_precedence_over_inconclusive(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="fail"),
                Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="inconclusive"),
                Evidence(id="EV-3", requirement_id="R3", kind="test", verdict="pass"),
            ],
        )
        path = tmp_path / "badge.json"
        export_shields_endpoint(report, path=path)
        data = json.loads(path.read_text())
        assert data["color"] == "red"
