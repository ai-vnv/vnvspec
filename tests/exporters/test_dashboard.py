"""Tests for the V&V dashboard exporter."""

from __future__ import annotations

from pathlib import Path

import pytest

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.exporters.dashboard import export_dashboard


@pytest.fixture()
def sample_spec() -> Spec:
    return Spec(
        name="dashboard-test",
        version="1.0",
        requirements=[
            Requirement(
                id="REQ-001",
                statement="The system shall validate inputs.",
                rationale="Safety.",
                verification_method="test",
                acceptance_criteria=["Invalid inputs rejected."],
                standards={"iso_pas_8800": ["6.2.1"]},
                metadata={"since": "0.1.0"},
            ),
            Requirement(
                id="REQ-002",
                statement="The system shall log errors.",
                rationale="Observability.",
                verification_method="test",
                acceptance_criteria=["Errors logged.", "Log format correct."],
                metadata={"since": "0.2.0"},
            ),
            Requirement(
                id="REQ-003",
                statement="The system shall respond within 100 ms.",
                rationale="Latency.",
                verification_method="test",
                acceptance_criteria=["p99 < 100 ms"],
                metadata={"since": "0.1.0"},
            ),
        ],
    )


@pytest.fixture()
def sample_report() -> Report:
    return Report(
        spec_name="dashboard-test",
        spec_version="1.0",
        evidence=[
            Evidence(
                id="EV-1",
                requirement_id="REQ-001",
                kind="test",
                verdict="pass",
                details={"source": "pytest", "test_name": "test_validate"},
            ),
            Evidence(
                id="EV-2",
                requirement_id="REQ-002",
                kind="test",
                verdict="fail",
                details={"source": "pytest", "test_name": "test_logging"},
            ),
        ],
    )


class TestDashboardExporter:
    def test_creates_index_html(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        result = export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        assert (result / "index.html").exists()

    def test_creates_requirement_pages(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        result = export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        for req in sample_spec.requirements:
            assert (result / "requirements" / f"{req.id}.html").exists()

    def test_creates_badge(self, sample_spec: Spec, sample_report: Report, tmp_path: Path) -> None:
        result = export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        badge = result / "badge.svg"
        assert badge.exists()
        assert "<svg" in badge.read_text()

    def test_index_contains_verdict(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "index.html").read_text()
        assert "FAIL" in html  # overall verdict since one evidence fails

    def test_index_contains_requirements_table(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "index.html").read_text()
        assert "REQ-001" in html
        assert "REQ-002" in html
        assert "REQ-003" in html

    def test_index_contains_standards(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "index.html").read_text()
        assert "Standards Compliance" in html
        assert "8800" in html

    def test_index_contains_version_traceability(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "index.html").read_text()
        assert "v0.1.0" in html
        assert "v0.2.0" in html

    def test_requirement_page_contains_evidence(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "requirements" / "REQ-001.html").read_text()
        assert "EV-1" in html
        assert "pass" in html

    def test_requirement_page_shows_since(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "requirements" / "REQ-001.html").read_text()
        assert "since 0.1.0" in html

    def test_requirement_page_shows_acceptance_criteria(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "requirements" / "REQ-002.html").read_text()
        assert "Errors logged." in html
        assert "Log format correct." in html

    def test_requirement_page_shows_standards_mapping(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "requirements" / "REQ-001.html").read_text()
        assert "iso_pas_8800" in html
        assert "6.2.1" in html

    def test_badge_with_dashboard_url(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(
            sample_spec,
            sample_report,
            output_dir=tmp_path / "dash",
            dashboard_url="https://example.com/dashboard/",
        )
        badge = (tmp_path / "dash" / "badge.svg").read_text()
        assert "https://example.com/dashboard/" in badge

    def test_history_timeline(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        old_report = Report(
            spec_name="dashboard-test",
            spec_version="0.9",
            evidence=[
                Evidence(id="EV-OLD-1", requirement_id="REQ-001", kind="test", verdict="fail"),
            ],
        )
        export_dashboard(
            sample_spec,
            sample_report,
            output_dir=tmp_path / "dash",
            history=[old_report],
        )
        html = (tmp_path / "dash" / "requirements" / "REQ-001.html").read_text()
        assert "Version History" in html
        assert "0.9" in html

    def test_uncovered_requirement_shows_inconclusive(
        self, sample_spec: Spec, sample_report: Report, tmp_path: Path
    ) -> None:
        export_dashboard(sample_spec, sample_report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "requirements" / "REQ-003.html").read_text()
        assert "No evidence collected" in html

    def test_spec_without_standards(self, tmp_path: Path) -> None:
        spec = Spec(
            name="no-standards",
            requirements=[
                Requirement(
                    id="REQ-001",
                    statement="Simple req.",
                    verification_method="test",
                    metadata={"since": "0.1.0"},
                ),
            ],
        )
        report = Report(spec_name="no-standards", evidence=[])
        export_dashboard(spec, report, output_dir=tmp_path / "dash")
        html = (tmp_path / "dash" / "index.html").read_text()
        assert "Standards Compliance" not in html

    def test_spec_with_unknown_standard(self, tmp_path: Path) -> None:
        spec = Spec(
            name="bad-std",
            requirements=[
                Requirement(
                    id="REQ-001",
                    statement="Simple req.",
                    verification_method="test",
                    standards={"nonexistent_standard_xyz": ["1.1"]},
                    metadata={"since": "0.1.0"},
                ),
            ],
        )
        report = Report(spec_name="bad-std", evidence=[])
        # Should not crash on unknown standard
        export_dashboard(spec, report, output_dir=tmp_path / "dash")
        assert (tmp_path / "dash" / "index.html").exists()
