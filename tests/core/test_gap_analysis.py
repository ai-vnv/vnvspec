"""Tests for standard_gap_analysis."""

from __future__ import annotations

from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.core.trace import standard_gap_analysis


class TestStandardGapAnalysis:
    def test_empty_spec_all_gaps(self) -> None:
        spec = Spec(name="empty")
        report = standard_gap_analysis(spec, "iso_pas_8800")
        assert report.gaps > 0
        assert report.covered == 0
        assert report.total_clauses == report.gaps

    def test_covered_clause(self) -> None:
        req = Requirement(
            id="REQ-001",
            statement="The system shall define safety goals.",
            rationale="ISO/PAS 8800 compliance.",
            verification_method="analysis",
            acceptance_criteria=["Safety goals documented."],
            standards={"iso_pas_8800": ["6.2.1"]},
        )
        spec = Spec(name="test", requirements=[req])
        report = standard_gap_analysis(spec, "iso_pas_8800")
        covered_clauses = [c for c in report.clauses if c.status == "covered"]
        assert len(covered_clauses) >= 1
        assert any("REQ-001" in c.mapped_requirements for c in covered_clauses)

    def test_gap_clause(self) -> None:
        spec = Spec(name="test")
        report = standard_gap_analysis(spec, "iso_pas_8800")
        gap_clauses = [c for c in report.clauses if c.status == "gap"]
        assert len(gap_clauses) > 0

    def test_standard_name_in_report(self) -> None:
        spec = Spec(name="test")
        report = standard_gap_analysis(spec, "iso_pas_8800")
        assert "8800" in report.standard

    def test_clause_details(self) -> None:
        spec = Spec(name="test")
        report = standard_gap_analysis(spec, "iso_pas_8800")
        for clause in report.clauses:
            assert clause.clause != ""
            assert clause.title != ""
            assert clause.normative_level in ("shall", "should")
