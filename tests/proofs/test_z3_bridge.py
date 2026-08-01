"""Tests for the Z3 formal verification proof bridge.

All tests require z3-solver and skip gracefully if z3 is not installed.
"""

from __future__ import annotations

import pytest

z3 = pytest.importorskip("z3", reason="z3-solver not installed")

from vnvspec.core.evidence import Evidence
from vnvspec.proofs.z3_bridge import (
    ProofResult,
    verify_numeric_range,
    verify_z3_formula,
)


class TestVerifyNumericRangeProved:
    def test_proved_under_system_assumptions(self) -> None:
        p = z3.Real("probability")
        system_assumptions = [p >= 0.1, p <= 0.9]

        result, ev = verify_numeric_range(
            var_name="probability",
            var_type="real",
            min_val=0.0,
            max_val=1.0,
            assumptions=system_assumptions,
            requirement_id="REQ-PROB-001",
        )
        assert result.status == "proved"
        assert result.verdict == "pass"
        assert result.counterexample is None
        assert isinstance(ev, Evidence)
        assert ev.kind == "formal_proof"
        assert ev.verdict == "pass"
        assert ev.requirement_id == "REQ-PROB-001"
        assert result.solver_time_ms >= 0.0

    def test_integer_range_proved(self) -> None:
        x = z3.Int("count")
        result, _ev = verify_numeric_range(
            var_name="count",
            var_type="int",
            min_val=0,
            max_val=100,
            assumptions=[x >= 1, x <= 50],
            requirement_id="REQ-INT-001",
        )
        assert result.status == "proved"
        assert result.verdict == "pass"

    def test_one_sided_lower_bound_only(self) -> None:
        x = z3.Real("x")
        result, _ev = verify_numeric_range(
            var_name="x",
            var_type="real",
            min_val=0.0,
            assumptions=[x >= 5.0],
            requirement_id="REQ-LOWER",
        )
        assert result.status == "proved"

    def test_one_sided_upper_bound_only(self) -> None:
        x = z3.Real("x")
        result, _ev = verify_numeric_range(
            var_name="x",
            var_type="real",
            max_val=100.0,
            assumptions=[x <= 50.0],
            requirement_id="REQ-UPPER",
        )
        assert result.status == "proved"


class TestVerifyNumericRangeDisproved:
    def test_disproved_via_formula(self) -> None:
        solver = z3.Solver()
        x = z3.Real("x")
        solver.add(x == 5.0)
        solver.add(z3.Not(x <= 3.0))

        result, ev = verify_z3_formula(solver, requirement_id="REQ-BOUND-001")
        assert result.status == "disproved"
        assert result.verdict == "fail"
        assert result.counterexample is not None
        assert "x" in result.counterexample
        assert ev.kind == "formal_proof"
        assert ev.verdict == "fail"


class TestTrivialInvariant:
    def test_no_bounds_returns_proved(self) -> None:
        result, ev = verify_numeric_range(
            var_name="x",
            var_type="real",
            requirement_id="REQ-TRIVIAL",
        )
        assert result.status == "proved"
        assert result.verdict == "pass"
        assert result.solver_time_ms == 0.0
        assert ev.verdict == "pass"


class TestInputValidation:
    def test_invalid_range_bounds_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="Invalid range bounds"):
            verify_numeric_range(
                var_name="x",
                var_type="real",
                min_val=10.0,
                max_val=5.0,
            )

    def test_negative_timeout_raises_value_error(self) -> None:
        solver = z3.Solver()
        with pytest.raises(ValueError, match="timeout_ms must be positive"):
            verify_z3_formula(solver, requirement_id="REQ-001", timeout_ms=-10)

    def test_zero_timeout_raises_value_error(self) -> None:
        solver = z3.Solver()
        with pytest.raises(ValueError, match="timeout_ms must be positive"):
            verify_z3_formula(solver, requirement_id="REQ-001", timeout_ms=0)

    def test_overflow_timeout_raises_value_error(self) -> None:
        solver = z3.Solver()
        with pytest.raises(ValueError, match="exceeds Z3 maximum"):
            verify_z3_formula(solver, requirement_id="REQ-001", timeout_ms=2_147_483_648)


class TestTimeout:
    def test_timeout_parameter_accepted(self) -> None:
        p = z3.Real("p")
        result, _ev = verify_numeric_range(
            var_name="p",
            var_type="real",
            min_val=0.0,
            max_val=1.0,
            assumptions=[p >= 0.1, p <= 0.9],
            timeout_ms=5000,
        )
        assert result.status == "proved"
        assert result.verdict == "pass"


class TestModelExtractionResilience:
    def test_uninterpreted_function_in_model(self) -> None:
        """Verify that a sat model containing uninterpreted functions
        does not crash counterexample extraction."""
        solver = z3.Solver()
        f = z3.Function("f", z3.IntSort(), z3.IntSort())
        x = z3.Int("x")
        # Satisfiable: f(x) == 10 has a model (x can be anything, f maps x to 10)
        solver.add(f(x) == 10)
        # Negate: x != 0 (so solver picks some x and f(x)=10)
        solver.add(z3.Not(x == 0))

        result, ev = verify_z3_formula(solver, requirement_id="REQ-FUNC")
        assert result.status == "disproved"
        assert result.counterexample is not None
        # The function declaration should be extracted without crashing
        assert "f" in result.counterexample
        assert "<function/" in result.counterexample["f"]
        assert ev.verdict == "fail"


class TestProofResultSerialization:
    def test_to_evidence_roundtrip(self) -> None:
        result = ProofResult(
            status="proved",
            verdict="pass",
            solver_time_ms=1.5,
            message="All assertions unsat.",
        )
        ev = result.to_evidence(requirement_id="REQ-001")
        d = ev.model_dump()
        ev2 = Evidence.model_validate(d)
        assert ev == ev2
        assert ev2.details["status"] == "proved"
        assert ev2.details["solver_time_ms"] == 1.5

    def test_default_evidence_id_generation(self) -> None:
        result = ProofResult(
            status="proved",
            verdict="pass",
            solver_time_ms=0.1,
        )
        ev = result.to_evidence(requirement_id="REQ-042")
        assert ev.id == "EV-PROOF-REQ-042"

    def test_custom_evidence_id(self) -> None:
        result = ProofResult(
            status="proved",
            verdict="pass",
            solver_time_ms=0.1,
        )
        ev = result.to_evidence(requirement_id="REQ-042", evidence_id="EV-CUSTOM-001")
        assert ev.id == "EV-CUSTOM-001"

    def test_counterexample_in_details(self) -> None:
        result = ProofResult(
            status="disproved",
            verdict="fail",
            solver_time_ms=2.0,
            counterexample={"x": "5"},
            message="Violation found.",
        )
        ev = result.to_evidence(requirement_id="REQ-001")
        assert ev.details["counterexample"] == {"x": "5"}
        assert ev.details["message"] == "Violation found."
