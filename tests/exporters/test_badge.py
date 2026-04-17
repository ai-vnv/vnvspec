"""Tests for the badge exporter."""

from __future__ import annotations

from pathlib import Path

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.badge import export_badge


class TestBadgeExporter:
    def test_pass_badge(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
                Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="pass"),
            ],
        )
        path = tmp_path / "badge.svg"
        result = export_badge(report, path=path)
        assert result == path
        assert path.exists()
        content = path.read_text()
        assert "<svg" in content
        assert "PASS" in content
        assert "#4c1" in content  # green

    def test_fail_badge(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
                Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="fail"),
            ],
        )
        path = tmp_path / "badge.svg"
        export_badge(report, path=path)
        content = path.read_text()
        assert "FAIL" in content
        assert "#e05d44" in content  # red

    def test_inconclusive_badge(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="inconclusive"),
            ],
        )
        path = tmp_path / "badge.svg"
        export_badge(report, path=path)
        content = path.read_text()
        assert "INCONCLUSIVE" in content

    def test_empty_badge(self, tmp_path: Path) -> None:
        report = Report(spec_name="test")
        path = tmp_path / "badge.svg"
        export_badge(report, path=path)
        content = path.read_text()
        assert "N/A" in content

    def test_svg_valid_structure(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
            ],
        )
        path = tmp_path / "badge.svg"
        export_badge(report, path=path)
        content = path.read_text()
        assert content.startswith("<svg")
        assert "</svg>" in content
