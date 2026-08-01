"""Example script demonstrating ISO/IEC 42001 AIMS catalog usage in vnvspec.

Loads ISO/IEC 42001 management system controls and Annex A controls into a Spec,
validates quality, and executes standard_gap_analysis against the bundled ISO 42001 registry.
"""

from vnvspec import Spec
from vnvspec.catalog.standards.iso_42001 import annex_a_controls, management_controls
from vnvspec.core.trace import standard_gap_analysis


def main() -> None:
    print("=== vnvspec ISO/IEC 42001 AIMS Catalog Demo ===")

    # 1. Instantiate spec with ISO 42001 requirements
    reqs = management_controls() + annex_a_controls()
    spec = Spec(
        name="enterprise-ai-aims-spec",
        description="Specification for Enterprise AI Management System (ISO/IEC 42001)",
        requirements=reqs,
    )

    print(f"Spec Name: {spec.name}")
    print(f"Total Requirements: {len(spec.requirements)}")

    # 2. Perform standard gap analysis
    report = standard_gap_analysis(spec, "iso_42001")
    coverage_pct = (report.covered / report.total_clauses) * 100 if report.total_clauses else 0.0
    print(f"Standards Coverage: {coverage_pct:.1f}%")
    print(f"Covered Clauses: {report.covered} / {report.total_clauses}")
    print(f"Gaps Identified: {report.gaps}")

    print("\nSample Clauses Analysis:")
    for clause in report.clauses[:5]:
        status = "COVERED" if clause.status == "covered" else "GAP"
        req_ids = clause.mapped_requirements
        print(f" - [{status}] Clause {clause.clause} ({clause.title}) -> Reqs: {req_ids}")


if __name__ == "__main__":
    main()
