"""Tests for the EU AI Act Annex IV exporter."""

from __future__ import annotations

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.exporters.techdoc_annex_iv import export_annex_iv


def _sample_report() -> Report:
    return Report(
        spec_name="test-spec",
        spec_version="1.0",
        evidence=[
            Evidence(id="EV-1", requirement_id="REQ-1", kind="test", verdict="pass"),
            Evidence(id="EV-2", requirement_id="REQ-2", kind="analysis", verdict="fail"),
        ],
        summary={"accuracy": 0.95},
    )


def test_annex_iv_contains_heading() -> None:
    doc = export_annex_iv(_sample_report())
    assert "Annex IV" in doc


def test_annex_iv_contains_spec_name() -> None:
    doc = export_annex_iv(_sample_report())
    assert "test-spec" in doc


def test_annex_iv_contains_sections() -> None:
    doc = export_annex_iv(_sample_report())
    assert "## 1. Intended Purpose" in doc
    assert "## 2. Design and Development" in doc
    assert "## 3. Performance Metrics" in doc
    assert "## 4. Risk Management" in doc
    assert "## 5. Monitoring" in doc


def test_annex_iv_evidence_table() -> None:
    doc = export_annex_iv(_sample_report())
    assert "EV-1" in doc
    assert "EV-2" in doc
    assert "pass" in doc
    assert "fail" in doc


def test_annex_iv_summary_metrics() -> None:
    doc = export_annex_iv(_sample_report())
    assert "accuracy" in doc


def test_annex_iv_empty_report() -> None:
    doc = export_annex_iv(Report(spec_name="empty", spec_version="0.0"))
    assert "empty" in doc
    assert "inconclusive" in doc
