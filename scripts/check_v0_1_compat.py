#!/usr/bin/env python3
"""Verify that all v0.1.0 public symbols are still importable.

This script enforces the backward-compatibility contract: every symbol
exported from vnvspec.__init__ at v0.1.0 must remain importable with
the same behavior in v0.2.0+.

Exit code 0 = all symbols present. Non-zero = regression.
"""

from __future__ import annotations

import sys

# Symbols exported by vnvspec v0.1.0
V0_1_SYMBOLS = [
    "ODD",
    "AssessmentError",
    "ContractError",
    "Evidence",
    "Hazard",
    "IOContract",
    "Invariant",
    "Requirement",
    "RequirementError",
    "Spec",
    "SpecError",
    "TraceLink",
    "VnvspecError",
    "__version__",
    "build_trace_graph",
    "coverage_report",
]


def main() -> int:
    import vnvspec

    missing: list[str] = []
    for symbol in V0_1_SYMBOLS:
        if not hasattr(vnvspec, symbol):
            missing.append(symbol)
            print(f"MISSING: vnvspec.{symbol}")

    if missing:
        print(f"\nFAILED: {len(missing)} v0.1 symbol(s) missing from vnvspec")
        return 1

    print(f"OK: all {len(V0_1_SYMBOLS)} v0.1 symbols still importable")

    # Verify basic behavior
    spec = vnvspec.Spec(name="compat-test")
    assert spec.name == "compat-test"

    req = vnvspec.Requirement(id="REQ-001", statement="Test.", verification_method="test")
    assert req.id == "REQ-001"

    ev = vnvspec.Evidence(id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass")
    assert ev.verdict == "pass"

    link = vnvspec.TraceLink(source_id="A", target_id="B", relation="verifies")
    assert link.relation == "verifies"

    print("OK: basic behavioral checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
