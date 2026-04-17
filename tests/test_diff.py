"""Tests for report diff (evidence regression detection)."""

from __future__ import annotations

import pytest

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.diff import compare_reports


def _make_report(*ev_tuples: tuple[str, str]) -> Report:
    """Helper: create report from (req_id, verdict) tuples."""
    evidence = [
        Evidence(id=f"EV-{i}", requirement_id=req_id, kind="test", verdict=verdict)
        for i, (req_id, verdict) in enumerate(ev_tuples, 1)
    ]
    return Report(spec_name="test", evidence=evidence)


class TestCompareReports:
    def test_identical_reports(self) -> None:
        r = _make_report(("R1", "pass"), ("R2", "pass"))
        diff = compare_reports(r, r)
        assert diff.new_failures == []
        assert diff.new_passes == []
        assert diff.regressions == []
        assert diff.added_requirements == []
        assert diff.removed_requirements == []

    @pytest.mark.vnvspec("REQ-SELF-DIFF-001")
    def test_regression_detected(self) -> None:
        prev = _make_report(("R1", "pass"), ("R2", "pass"))
        curr = _make_report(("R1", "pass"), ("R2", "fail"))
        diff = compare_reports(prev, curr)
        assert "R2" in diff.regressions
        assert "R2" in diff.new_failures

    def test_new_pass(self) -> None:
        prev = _make_report(("R1", "fail"))
        curr = _make_report(("R1", "pass"))
        diff = compare_reports(prev, curr)
        assert "R1" in diff.new_passes
        assert diff.regressions == []

    def test_new_failure_from_inconclusive(self) -> None:
        prev = _make_report(("R1", "inconclusive"))
        curr = _make_report(("R1", "fail"))
        diff = compare_reports(prev, curr)
        assert "R1" in diff.new_failures
        assert "R1" not in diff.regressions  # not a regression from pass

    def test_added_requirement(self) -> None:
        prev = _make_report(("R1", "pass"))
        curr = _make_report(("R1", "pass"), ("R2", "pass"))
        diff = compare_reports(prev, curr)
        assert "R2" in diff.added_requirements

    def test_removed_requirement(self) -> None:
        prev = _make_report(("R1", "pass"), ("R2", "pass"))
        curr = _make_report(("R1", "pass"))
        diff = compare_reports(prev, curr)
        assert "R2" in diff.removed_requirements

    def test_reorder_does_not_affect(self) -> None:
        prev = _make_report(("R1", "pass"), ("R2", "fail"))
        curr = _make_report(("R2", "fail"), ("R1", "pass"))
        diff = compare_reports(prev, curr)
        assert diff.regressions == []
        assert diff.new_failures == []
        assert diff.new_passes == []

    def test_empty_reports(self) -> None:
        prev = Report(spec_name="test")
        curr = Report(spec_name="test")
        diff = compare_reports(prev, curr)
        assert diff.new_failures == []
        assert diff.regressions == []
