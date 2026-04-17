"""Tests for the GSN Mermaid exporter."""

from __future__ import annotations

from datetime import UTC, datetime

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.gsn_mermaid import export_gsn_mermaid


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


def test_mermaid_non_empty() -> None:
    mmd = export_gsn_mermaid(_sample_report())
    assert len(mmd) > 0


def test_mermaid_starts_with_flowchart() -> None:
    mmd = export_gsn_mermaid(_sample_report())
    assert mmd.startswith("flowchart TD")


def test_mermaid_contains_requirement_ids() -> None:
    mmd = export_gsn_mermaid(_sample_report())
    assert "REQ-001" in mmd
    assert "REQ-002" in mmd


def test_mermaid_contains_verdicts() -> None:
    mmd = export_gsn_mermaid(_sample_report())
    assert "pass" in mmd
    assert "fail" in mmd


def test_mermaid_contains_edges() -> None:
    mmd = export_gsn_mermaid(_sample_report())
    assert "-->" in mmd


def test_mermaid_empty_report() -> None:
    r = Report(spec_name="empty")
    mmd = export_gsn_mermaid(r)
    assert "flowchart TD" in mmd
    assert "inconclusive" in mmd
