"""Example script demonstrating Z3 formal verification proof bridge in vnvspec.

Runs Z3 invariant verification, generates ProofResult objects, converts them to
Evidence(kind="formal_proof"), and attaches them to a Spec report.
"""

import sys

from vnvspec import Requirement, Spec
from vnvspec.proofs import verify_numeric_range, verify_z3_formula

try:
    import z3
except ImportError:
    print("z3-solver is required to run this example. Install via: pip install z3-solver")
    sys.exit(0)


def main() -> None:
    print("=== vnvspec Z3 Formal Verification Proof Bridge Demo ===")

    # 1. Define requirement
    req = Requirement(
        id="REQ-FORMAL-001",
        statement="The probability output shall remain bounded strictly within [0.0, 1.0].",
        rationale="Model outputs used in safety decisions must be valid probabilities.",
        verification_method="formal_proof",
        acceptance_criteria=["Formal proof showing 0.0 <= p <= 1.0 under all valid inputs."],
    )

    spec = Spec(name="formal-verification-spec", requirements=[req])
    print(f"Spec Name: {spec.name}")

    # 2. Run numerical range proof for probability variable under system model bounds
    p = z3.Real("probability")
    min_prob, max_prob = 0.05, 0.95
    system_assumptions = [p >= min_prob, p <= max_prob]

    result, evidence = verify_numeric_range(
        var_name="probability",
        var_type="real",
        min_val=0.0,
        max_val=1.0,
        assumptions=system_assumptions,
        requirement_id=req.id,
    )

    print(f"\nProof Status: {result.status}")
    print(f"Evidence Verdict: {evidence.verdict}")
    print(f"Evidence Kind: {evidence.kind}")
    print(f"Solver Time: {result.solver_time_ms:.2f} ms")
    print(f"Message: {result.message}")

    # 3. Demonstrate counterexample extraction on a violated invariant
    solver = z3.Solver()
    speed = z3.Real("speed")
    target_speed, max_speed = 120.0, 100.0
    solver.add(speed == target_speed)  # System state assumption
    solver.add(z3.Not(speed <= max_speed))  # Negation of safety constraint (speed <= 100)

    res_fail, ev_fail = verify_z3_formula(solver, requirement_id="REQ-SPEED-001")
    print(f"\nViolated Invariant Proof Status: {res_fail.status}")
    print(f"Violated Evidence Verdict: {ev_fail.verdict}")
    print(f"Counterexample Extracted: {res_fail.counterexample}")


if __name__ == "__main__":
    main()
