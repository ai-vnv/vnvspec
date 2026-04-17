"""Tests for EvidenceCollector context manager."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from vnvspec.collectors import EvidenceCollector
from vnvspec.core.errors import RequirementError
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec


@pytest.fixture()
def sample_spec() -> Spec:
    return Spec(
        name="test-spec",
        version="1.0",
        requirements=[
            Requirement(
                id="REQ-001",
                statement="The system shall produce valid outputs.",
                rationale="Safety.",
                verification_method="test",
                acceptance_criteria=["All outputs valid."],
            ),
            Requirement(
                id="REQ-002",
                statement="The system shall respond within 100 ms.",
                rationale="Latency.",
                verification_method="test",
                acceptance_criteria=["p99 < 100 ms"],
            ),
            Requirement(
                id="REQ-003",
                statement="The system shall log all requests.",
                rationale="Audit.",
                verification_method="inspection",
                acceptance_criteria=["Logs exist."],
            ),
        ],
    )


class TestEvidenceCollectorContextManager:
    def test_context_manager_lifecycle(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as collector:
            collector.check("REQ-001", True, message="all good")
        assert len(collector._evidence) == 1

    def test_check_pass(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            ev = c.check("REQ-001", True, message="passed")
        assert ev.verdict == "pass"
        assert ev.details["message"] == "passed"

    def test_check_fail(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            ev = c.check("REQ-001", False, message="failed")
        assert ev.verdict == "fail"

    def test_check_with_extra_details(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            ev = c.check("REQ-001", True, message="ok", accuracy=0.95, dataset="test")
        assert ev.details["accuracy"] == 0.95
        assert ev.details["dataset"] == "test"

    def test_record_explicit_verdict(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            ev = c.record("REQ-003", "pass", kind="inspection", message="logs verified")
        assert ev.verdict == "pass"
        assert ev.kind == "inspection"

    def test_record_inconclusive(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            ev = c.record("REQ-002", "inconclusive", message="needs more data")
        assert ev.verdict == "inconclusive"

    def test_unknown_requirement_raises(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            with pytest.raises(RequirementError, match="REQ-999"):
                c.check("REQ-999", True)

    def test_unknown_requirement_record_raises(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            with pytest.raises(RequirementError, match="REQ-999"):
                c.record("REQ-999", "pass")

    def test_auto_ids_increment(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            ev1 = c.check("REQ-001", True)
            ev2 = c.check("REQ-002", True)
        assert ev1.id == "EV-AUTO-0001"
        assert ev2.id == "EV-AUTO-0002"

    def test_default_kind(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec, default_kind="analysis") as c:
            ev = c.check("REQ-001", True)
        assert ev.kind == "analysis"


class TestBuildReport:
    def test_auto_summary(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            c.check("REQ-001", True)
            c.check("REQ-002", False)
            c.record("REQ-003", "inconclusive")
        report = c.build_report()
        assert report.spec_name == "test-spec"
        assert report.summary["total"] == 3
        assert report.summary["pass"] == 1
        assert report.summary["fail"] == 1
        assert report.summary["inconclusive"] == 1

    def test_str_summary(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            c.check("REQ-001", True)
        report = c.build_report(summary="all good")
        assert report.summary == {"message": "all good"}

    def test_dict_summary(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            c.check("REQ-001", True)
        report = c.build_report(summary={"status": "ok"})
        assert report.summary == {"status": "ok"}

    def test_report_verdict(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            c.check("REQ-001", True)
            c.check("REQ-002", True)
        report = c.build_report()
        assert report.verdict() == "pass"

    def test_report_verdict_fail(self, sample_spec: Spec) -> None:
        with EvidenceCollector(sample_spec) as c:
            c.check("REQ-001", True)
            c.check("REQ-002", False)
        report = c.build_report()
        assert report.verdict() == "fail"


class TestJUnitXMLParsing:
    def test_parse_happy_path(self, sample_spec: Spec, tmp_path: Path) -> None:
        junit_xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <testsuite name="pytest" tests="2">
                <testcase classname="tests.test_core" name="test_valid_output" time="0.1">
                    <properties>
                        <property name="vnvspec" value="REQ-001" />
                    </properties>
                </testcase>
                <testcase classname="tests.test_core" name="test_latency" time="0.2">
                    <properties>
                        <property name="vnvspec" value="REQ-002" />
                    </properties>
                </testcase>
            </testsuite>
        """)
        xml_path = tmp_path / "results.xml"
        xml_path.write_text(junit_xml)

        with EvidenceCollector(sample_spec) as c:
            results = c.from_pytest_junit(xml_path)

        assert len(results) == 2
        assert results[0].verdict == "pass"
        assert results[1].verdict == "pass"
        assert results[0].requirement_id == "REQ-001"

    def test_parse_failure(self, sample_spec: Spec, tmp_path: Path) -> None:
        junit_xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <testsuite name="pytest" tests="1">
                <testcase classname="tests.test_core" name="test_fail" time="0.1">
                    <properties>
                        <property name="vnvspec" value="REQ-001" />
                    </properties>
                    <failure message="AssertionError">assert False</failure>
                </testcase>
            </testsuite>
        """)
        xml_path = tmp_path / "results.xml"
        xml_path.write_text(junit_xml)

        with EvidenceCollector(sample_spec) as c:
            results = c.from_pytest_junit(xml_path)

        assert len(results) == 1
        assert results[0].verdict == "fail"

    def test_parse_skipped(self, sample_spec: Spec, tmp_path: Path) -> None:
        junit_xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <testsuite name="pytest" tests="1">
                <testcase classname="tests.test_core" name="test_skip" time="0.0">
                    <properties>
                        <property name="vnvspec" value="REQ-001" />
                    </properties>
                    <skipped message="not ready" />
                </testcase>
            </testsuite>
        """)
        xml_path = tmp_path / "results.xml"
        xml_path.write_text(junit_xml)

        with EvidenceCollector(sample_spec) as c:
            results = c.from_pytest_junit(xml_path)

        assert len(results) == 1
        assert results[0].verdict == "inconclusive"

    def test_unknown_requirement_skipped(self, sample_spec: Spec, tmp_path: Path) -> None:
        junit_xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <testsuite name="pytest" tests="1">
                <testcase classname="tests.test_core" name="test_unknown" time="0.1">
                    <properties>
                        <property name="vnvspec" value="REQ-UNKNOWN" />
                    </properties>
                </testcase>
            </testsuite>
        """)
        xml_path = tmp_path / "results.xml"
        xml_path.write_text(junit_xml)

        with EvidenceCollector(sample_spec) as c:
            with pytest.warns(RuntimeWarning, match="REQ-UNKNOWN"):
                results = c.from_pytest_junit(xml_path)

        assert len(results) == 0

    def test_malformed_xml(self, sample_spec: Spec, tmp_path: Path) -> None:
        xml_path = tmp_path / "bad.xml"
        xml_path.write_text("<not valid xml")

        with EvidenceCollector(sample_spec) as c:
            with pytest.raises(RequirementError, match="Failed to parse"):
                c.from_pytest_junit(xml_path)

    def test_no_properties(self, sample_spec: Spec, tmp_path: Path) -> None:
        junit_xml = textwrap.dedent("""\
            <?xml version="1.0" encoding="utf-8"?>
            <testsuite name="pytest" tests="1">
                <testcase classname="tests.test_core" name="test_plain" time="0.1" />
            </testsuite>
        """)
        xml_path = tmp_path / "results.xml"
        xml_path.write_text(junit_xml)

        with EvidenceCollector(sample_spec) as c:
            results = c.from_pytest_junit(xml_path)

        assert len(results) == 0
