"""Tests for the HTML exporter."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.html import export_html


def _sample_report() -> Report:
    return Report(
        spec_name="test-system",
        spec_version="0.1.0",
        evidence=[
            Evidence(
                id="EV-001",
                requirement_id="REQ-001",
                kind="test",
                verdict="pass",
                observed_at=datetime(2026, 4, 1, tzinfo=UTC),
            ),
            Evidence(
                id="EV-002",
                requirement_id="REQ-002",
                kind="analysis",
                verdict="fail",
                observed_at=datetime(2026, 4, 2, tzinfo=UTC),
            ),
            Evidence(
                id="EV-003",
                requirement_id="REQ-001",
                kind="inspection",
                verdict="pass",
                observed_at=datetime(2026, 4, 3, tzinfo=UTC),
            ),
        ],
    )


def test_html_non_empty() -> None:
    html = export_html(_sample_report())
    assert len(html) > 0


def test_html_structure() -> None:
    html = export_html(_sample_report())
    assert "<html" in html
    assert "</html>" in html
    assert "<style>" in html


def test_html_contains_requirement_ids() -> None:
    html = export_html(_sample_report())
    assert "REQ-001" in html
    assert "REQ-002" in html


def test_html_contains_verdicts() -> None:
    html = export_html(_sample_report())
    assert "pass" in html
    assert "fail" in html


def test_html_contains_evidence_ids() -> None:
    html = export_html(_sample_report())
    assert "EV-001" in html
    assert "EV-002" in html
    assert "EV-003" in html


def test_html_sorted_by_requirement(tmp_path: object) -> None:
    html = export_html(_sample_report())
    pos_req1 = html.index("REQ-001")
    pos_req2 = html.index("REQ-002")
    assert pos_req1 < pos_req2


def test_html_write_to_file(tmp_path: Path) -> None:
    out = tmp_path / "report.html"
    result = export_html(_sample_report(), path=out)
    assert out.read_text(encoding="utf-8") == result
