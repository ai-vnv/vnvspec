"""Tests for AssessmentContext and Report."""

from __future__ import annotations

import json

from vnvspec.core.assessment import AssessmentContext, Report
from vnvspec.core.evidence import Evidence


class TestAssessmentContext:
    def test_construction(self) -> None:
        ctx = AssessmentContext(run_id="run-001")
        assert ctx.run_id == "run-001"

    def test_defaults(self) -> None:
        ctx = AssessmentContext()
        assert ctx.run_id == ""
        assert ctx.metadata == {}


class TestReport:
    def test_empty_report(self) -> None:
        report = Report(spec_name="test", spec_version="1.0")
        assert report.spec_name == "test"
        assert len(report.evidence) == 0

    def test_pass_count(self) -> None:
        ev1 = Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass")
        ev2 = Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="fail")
        ev3 = Evidence(id="EV-3", requirement_id="R3", kind="test", verdict="pass")
        report = Report(spec_name="test", evidence=[ev1, ev2, ev3])
        assert report.pass_count() == 2

    def test_fail_count(self) -> None:
        ev1 = Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="fail")
        ev2 = Evidence(id="EV-2", requirement_id="R2", kind="test", verdict="fail")
        report = Report(spec_name="test", evidence=[ev1, ev2])
        assert report.fail_count() == 2

    def test_verdict_pass(self) -> None:
        ev = Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass")
        report = Report(spec_name="test", evidence=[ev])
        assert report.verdict() == "pass"

    def test_verdict_fail(self) -> None:
        ev = Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="fail")
        report = Report(spec_name="test", evidence=[ev])
        assert report.verdict() == "fail"

    def test_verdict_inconclusive(self) -> None:
        report = Report(spec_name="test")
        assert report.verdict() == "inconclusive"

    def test_json_round_trip(self) -> None:
        ev = Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass")
        report = Report(spec_name="test", evidence=[ev])
        data = json.loads(report.model_dump_json())
        report2 = Report.model_validate(data)
        assert report2.spec_name == "test"
        assert len(report2.evidence) == 1
