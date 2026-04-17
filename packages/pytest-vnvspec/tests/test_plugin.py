"""Tests for the pytest-vnvspec plugin using pytester."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


SAMPLE_SPEC_YAML = """\
name: test-spec
version: "1.0"
requirements:
  - id: REQ-001
    statement: The system shall produce valid outputs.
    rationale: Safety.
    verification_method: test
    acceptance_criteria:
      - All outputs valid.
  - id: REQ-002
    statement: The system shall respond within 100 ms.
    rationale: Latency.
    verification_method: test
    acceptance_criteria:
      - p99 < 100 ms
  - id: REQ-003
    statement: The system shall log all requests.
    rationale: Audit.
    verification_method: inspection
    acceptance_criteria:
      - Logs exist.
  - id: REQ-004
    statement: The system shall handle errors gracefully.
    rationale: Robustness.
    priority: blocking
    verification_method: test
    acceptance_criteria:
      - No unhandled exceptions.
"""


@pytest.fixture()
def spec_file(pytester: pytest.Pytester) -> Path:
    """Create a sample spec file in the test directory."""
    spec_path = pytester.path / "spec.yaml"
    spec_path.write_text(SAMPLE_SPEC_YAML)
    return spec_path


class TestMarkerResolution:
    def test_marker_pass(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_valid():
                assert True
        """)
        result = pytester.runpytest(f"--vnvspec-spec={spec_file}")
        result.assert_outcomes(passed=1)

    def test_marker_fail(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_invalid():
                assert False
        """)
        result = pytester.runpytest(f"--vnvspec-spec={spec_file}")
        result.assert_outcomes(failed=1)

    def test_unknown_marker_warns(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-UNKNOWN")
            def test_unknown():
                assert True
        """)
        result = pytester.runpytest(f"--vnvspec-spec={spec_file}", "-W", "error::pytest.PytestUnknownMarkWarning")
        # The test should still pass but with a warning
        # When -W error is set, it will cause failure
        assert result.ret != 0 or "REQ-UNKNOWN" in result.stdout.str()


class TestEvidenceCapture:
    def test_report_generation(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        report_path = pytester.path / "report.json"
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_one():
                assert True

            @pytest.mark.vnvspec("REQ-002")
            def test_two():
                assert True
        """)
        pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            f"--vnvspec-report={report_path}",
        )
        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert data["spec_name"] == "test-spec"
        assert len(data["evidence"]) >= 2

    def test_pass_evidence(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        report_path = pytester.path / "report.json"
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_pass():
                assert True
        """)
        pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            f"--vnvspec-report={report_path}",
        )
        data = json.loads(report_path.read_text())
        pass_ev = [e for e in data["evidence"] if e["requirement_id"] == "REQ-001"]
        assert len(pass_ev) >= 1
        assert pass_ev[0]["verdict"] == "pass"

    def test_fail_evidence(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        report_path = pytester.path / "report.json"
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_fail():
                assert False
        """)
        pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            f"--vnvspec-report={report_path}",
        )
        data = json.loads(report_path.read_text())
        fail_ev = [e for e in data["evidence"] if e["requirement_id"] == "REQ-001"]
        assert len(fail_ev) >= 1
        assert fail_ev[0]["verdict"] == "fail"

    def test_inconclusive_for_unlinked_reqs(
        self, pytester: pytest.Pytester, spec_file: Path
    ) -> None:
        report_path = pytester.path / "report.json"
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_one():
                assert True
        """)
        pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            f"--vnvspec-report={report_path}",
        )
        data = json.loads(report_path.read_text())
        # REQ-002 and REQ-004 are verification_method="test" but have no linked test
        inconclusive = [
            e for e in data["evidence"]
            if e["verdict"] == "inconclusive"
        ]
        assert len(inconclusive) >= 2

    def test_multiple_markers(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        report_path = pytester.path / "report.json"
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            @pytest.mark.vnvspec("REQ-002")
            def test_both():
                assert True
        """)
        pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            f"--vnvspec-report={report_path}",
        )
        data = json.loads(report_path.read_text())
        req_001_ev = [e for e in data["evidence"] if e["requirement_id"] == "REQ-001" and e["verdict"] == "pass"]
        req_002_ev = [e for e in data["evidence"] if e["requirement_id"] == "REQ-002" and e["verdict"] == "pass"]
        assert len(req_001_ev) >= 1
        assert len(req_002_ev) >= 1


class TestFailOnPolicy:
    def test_fail_on_never(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_fail():
                assert False
        """)
        result = pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            "--vnvspec-fail-on=never",
        )
        # Test itself fails, but vnvspec doesn't add extra failure
        result.assert_outcomes(failed=1)

    def test_no_spec_no_plugin(self, pytester: pytest.Pytester) -> None:
        """Without --vnvspec-spec, plugin should not interfere."""
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_pass():
                assert True
        """)
        result = pytester.runpytest()
        result.assert_outcomes(passed=1)


class TestReportSummary:
    def test_summary_counts(self, pytester: pytest.Pytester, spec_file: Path) -> None:
        report_path = pytester.path / "report.json"
        pytester.makepyfile("""
            import pytest

            @pytest.mark.vnvspec("REQ-001")
            def test_pass():
                assert True

            @pytest.mark.vnvspec("REQ-002")
            def test_fail():
                assert False
        """)
        pytester.runpytest(
            f"--vnvspec-spec={spec_file}",
            f"--vnvspec-report={report_path}",
        )
        data = json.loads(report_path.read_text())
        summary = data["summary"]
        assert summary["pass"] >= 1
        assert summary["fail"] >= 1
        assert "total" in summary
