#!/usr/bin/env python3
"""Verify that all v0.2.0 public symbols and behaviors are preserved.

This script enforces the backward-compatibility contract: every symbol
exported from vnvspec.__init__ at v0.2.0 must remain importable with
the same behavior in v0.3.0+.

Exit code 0 = all checks pass. Non-zero = regression.
"""

from __future__ import annotations

import sys

# Symbols exported by vnvspec v0.2.0 (superset of v0.1.0)
V0_2_SYMBOLS = [
    "ODD",
    "AssessmentError",
    "ContractError",
    "Evidence",
    "EvidenceCollector",
    "GapReport",
    "Hazard",
    "IOContract",
    "Invariant",
    "Report",
    "Requirement",
    "RequirementError",
    "Spec",
    "SpecError",
    "TraceLink",
    "VnvspecError",
    "__version__",
    "build_trace_graph",
    "coverage_report",
    "standard_gap_analysis",
]


def main() -> int:
    import vnvspec

    missing: list[str] = []
    for symbol in V0_2_SYMBOLS:
        if not hasattr(vnvspec, symbol):
            missing.append(symbol)
            print(f"MISSING: vnvspec.{symbol}")

    if missing:
        print(f"\nFAILED: {len(missing)} v0.2 symbol(s) missing from vnvspec")
        return 1

    print(f"OK: all {len(V0_2_SYMBOLS)} v0.2 symbols still importable")

    # Verify basic v0.2 behaviors

    # 1. Spec.extend() returns a new instance
    spec = vnvspec.Spec(name="compat-test")
    req = vnvspec.Requirement(id="REQ-001", statement="Test.", verification_method="test")
    extended = spec.extend(req)
    assert extended is not spec
    assert len(extended.requirements) == 1
    assert len(spec.requirements) == 0

    # 2. Evidence.details auto-wraps str
    ev = vnvspec.Evidence(
        id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass", details="ok"
    )
    assert ev.details == {"message": "ok"}

    # 3. Report.summary auto-wraps str
    report = vnvspec.Report(spec_name="test", summary="ok")
    assert report.summary == {"message": "ok"}

    # 4. Report.verdict() returns correct values
    assert vnvspec.Report(spec_name="test").verdict() == "inconclusive"
    ev_pass = vnvspec.Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass")
    assert vnvspec.Report(spec_name="test", evidence=[ev_pass]).verdict() == "pass"

    # 5. EvidenceCollector exists and is constructible
    collector = vnvspec.EvidenceCollector(spec)
    assert collector is not None

    # 6. Requirement.source accepts str (auto-normalizes to list)
    req_with_source = vnvspec.Requirement(
        id="REQ-SRC", statement="Test.", source="https://example.com"
    )
    assert isinstance(req_with_source.source, list)

    # 7. ExitCode enum importable from CLI
    from vnvspec.cli.main import ExitCode

    expected_ok = 0
    expected_inconclusive = 2
    assert ExitCode.OK == expected_ok
    assert ExitCode.INCONCLUSIVE == expected_inconclusive

    print("OK: basic v0.2 behavioral checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
