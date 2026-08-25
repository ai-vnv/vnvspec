"""Tests for the Z3 formal verification proof bridge.

All tests require z3-solver and skip gracefully if z3 is not installed.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest

z3 = pytest.importorskip("z3", reason="z3-solver not installed")

from vnvspec.core.evidence import Evidence
from vnvspec.proofs.z3_bridge import (
    ProofResult,
    verify_numeric_range,
    verify_z3_formula,
)


class _StubSolver:
    """Solver stub returning a fixed check result, or raising on check()."""

    def __init__(self, result: Any = None, model: Any = None, error: Exception | None = None):
        self._result = result
        self._model = model
        self._error = error

    def set(self, *_args: Any, **_kwargs: Any) -> None:
        return None

    def check(self) -> Any:
        if self._error is not None:
            raise self._error
        return self._result

    def model(self) -> Any:
        return self._model


class _StubModel:
    """Model stub returning a fixed list of declarations."""

    def __init__(self, decls: list[Any], value: Any = None):
        self._decls = decls
        self._value = value

    def decls(self) -> list[Any]:
        return self._decls

    def __getitem__(self, _decl: Any) -> Any:
        return self._value


class _BrokenDecl:
    """Declaration whose arity() raises, to exercise extraction resilience."""

    def name(self) -> str:
        return "broken"

    def arity(self) -> int:
        raise RuntimeError("arity unavailable")


class _NullValueDecl:
    """Constant declaration whose model lookup yields None."""

    def name(self) -> str:
        return "unset"

    def arity(self) -> int:
        return 0


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

    def test_decl_evaluation_error_is_recorded_not_raised(self) -> None:
        """A declaration that fails to evaluate is annotated, not fatal."""
        solver = _StubSolver(z3.sat, model=_StubModel([_BrokenDecl()]))
        result, ev = verify_z3_formula(solver, requirement_id="REQ-BADDECL")
        assert result.status == "disproved"
        assert result.verdict == "fail"
        assert result.counterexample is not None
        assert "evaluation error" in result.counterexample["broken"]
        assert "arity unavailable" in result.counterexample["broken"]
        assert ev.verdict == "fail"

    def test_none_valued_constant_is_stringified(self) -> None:
        """A constant absent from the model serialises as "None", not a crash."""
        solver = _StubSolver(z3.sat, model=_StubModel([_NullValueDecl()], value=None))
        result, _ev = verify_z3_formula(solver, requirement_id="REQ-NULLVAL")
        assert result.status == "disproved"
        assert result.counterexample == {"unset": "None"}


class TestZ3Unavailable:
    def test_missing_z3_raises_helpful_import_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A missing z3-solver must fail with install guidance, not a bare ImportError."""
        monkeypatch.setitem(sys.modules, "z3", None)
        with pytest.raises(ImportError, match="z3-solver is required"):
            verify_z3_formula(_StubSolver(), requirement_id="REQ-NOZ3")

    def test_missing_z3_message_names_the_extra(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setitem(sys.modules, "z3", None)
        with pytest.raises(ImportError, match=r"vnvspec\[z3\]"):
            verify_numeric_range(var_name="x", var_type="real", min_val=0.0, max_val=1.0)


class TestSolverExecutionFailure:
    def test_check_exception_yields_error_status(self) -> None:
        """A crashing solver is inconclusive evidence, never a silent pass."""
        solver = _StubSolver(error=RuntimeError("solver crashed"))
        result, ev = verify_z3_formula(solver, requirement_id="REQ-CRASH")
        assert result.status == "error"
        assert result.verdict == "inconclusive"
        assert "solver crashed" in result.message
        assert result.solver_time_ms >= 0.0
        assert result.counterexample is None
        assert ev.kind == "formal_proof"
        assert ev.verdict == "inconclusive"
        assert ev.id == "EV-PROOF-REQ-CRASH"

    def test_check_exception_honours_custom_evidence_id(self) -> None:
        solver = _StubSolver(error=ValueError("bad assertion stack"))
        _result, ev = verify_z3_formula(
            solver, requirement_id="REQ-CRASH", evidence_id="EV-CUSTOM-CRASH"
        )
        assert ev.id == "EV-CUSTOM-CRASH"
        assert ev.verdict == "inconclusive"


class TestUnknownResult:
    def test_unknown_yields_inconclusive(self) -> None:
        """UNKNOWN must stay inconclusive — never upgraded to pass."""
        result, ev = verify_z3_formula(_StubSolver(z3.unknown), requirement_id="REQ-UNK")
        assert result.status == "unknown"
        assert result.verdict == "inconclusive"
        assert "UNKNOWN" in result.message
        assert "after" not in result.message
        assert ev.verdict == "inconclusive"

    def test_unknown_reports_timeout_in_message(self) -> None:
        result, _ev = verify_z3_formula(
            _StubSolver(z3.unknown), requirement_id="REQ-UNK", timeout_ms=250
        )
        assert result.status == "unknown"
        assert result.verdict == "inconclusive"
        assert "after 250 ms" in result.message


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
