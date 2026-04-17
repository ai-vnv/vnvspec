"""Tests for the Markdown exporter."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.markdown import export_markdown


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
        ],
    )


def test_markdown_non_empty() -> None:
    md = export_markdown(_sample_report())
    assert len(md) > 0


def test_markdown_has_heading() -> None:
    md = export_markdown(_sample_report())
    assert "# V&V Report" in md


def test_markdown_contains_requirement_ids() -> None:
    md = export_markdown(_sample_report())
    assert "REQ-001" in md
    assert "REQ-002" in md


def test_markdown_contains_verdicts() -> None:
    md = export_markdown(_sample_report())
    assert "pass" in md
    assert "fail" in md


def test_markdown_contains_table_header() -> None:
    md = export_markdown(_sample_report())
    assert "| ID |" in md


def test_markdown_write_to_file(tmp_path: Path) -> None:
    out = tmp_path / "report.md"
    result = export_markdown(_sample_report(), path=out)
    assert out.read_text(encoding="utf-8") == result
