"""Z3 SMT solver bridge for formal invariant verification.

Integrates formal verification proofs with the vnvspec Evidence model.
"""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, Field

from vnvspec.core.evidence import Evidence, Verdict

ProofStatus = Literal["proved", "disproved", "unknown", "error"]

_MAX_TIMEOUT_MS = 2_147_483_647  # Z3 uses unsigned 32-bit int for timeout


class ProofResult(BaseModel):
    """Result of a formal verification proof run."""

    model_config = {"frozen": True}

    status: ProofStatus = Field(
        description="Outcome of the SMT solver check: proved, disproved, unknown, error."
    )
    verdict: Verdict = Field(
        description="Verdict for vnvspec evidence: pass, fail, or inconclusive."
    )
    solver_time_ms: float = Field(description="Execution time of the SMT solver in milliseconds.")
    counterexample: dict[str, Any] | None = Field(
        default=None, description="Counterexample variable assignments if disproved."
    )
    message: str = Field(default="", description="Summary message or explanation.")

    def to_evidence(self, requirement_id: str, evidence_id: str = "") -> Evidence:
        """Convert this ProofResult into a vnvspec Evidence object.

        Parameters
        ----------
        requirement_id:
            ID of the requirement verified.
        evidence_id:
            Optional evidence ID (defaults to ``EV-PROOF-<req_id>``).
        """
        ev_id = evidence_id or f"EV-PROOF-{requirement_id}"
        return Evidence(
            id=ev_id,
            requirement_id=requirement_id,
            kind="formal_proof",
            verdict=self.verdict,
            details={
                "status": self.status,
                "solver_time_ms": round(self.solver_time_ms, 3),
                "counterexample": self.counterexample,
                "message": self.message,
            },
        )


def _check_z3_available() -> Any:
    """Import and return the z3 module, or raise ImportError."""
    try:
        import z3  # noqa: PLC0415

        return z3
    except ImportError as err:
        raise ImportError(
            "z3-solver is required for formal verification proofs. "
            "Install it via `pip install vnvspec[z3]` or `pip install z3-solver`."
        ) from err


def verify_z3_formula(
    solver: Any,
    requirement_id: str,
    evidence_id: str = "",
    timeout_ms: int | None = None,
) -> tuple[ProofResult, Evidence]:
    """Verify a Z3 solver formula representing a requirement invariant.

    The solver is expected to contain assertions for the system model and the
    NEGATION of the target invariant.

    If ``solver.check()`` returns ``unsat``, the invariant is PROVED (no
    counterexample violates it). If it returns ``sat``, the invariant is
    DISPROVED and a counterexample model is extracted safely.

    Parameters
    ----------
    solver:
        A ``z3.Solver`` instance. If *timeout_ms* is provided, the solver's
        timeout parameter will be mutated in-place.
    requirement_id:
        ID of the requirement being verified.
    evidence_id:
        Optional ID for the generated Evidence object.
    timeout_ms:
        Optional solver timeout in milliseconds. Must be a positive integer
        not exceeding 2,147,483,647 (Z3 unsigned 32-bit limit).
    """
    z3 = _check_z3_available()

    if timeout_ms is not None:
        if timeout_ms <= 0:
            raise ValueError(f"timeout_ms must be positive, got {timeout_ms}")
        if timeout_ms > _MAX_TIMEOUT_MS:
            raise ValueError(f"timeout_ms exceeds Z3 maximum ({_MAX_TIMEOUT_MS}), got {timeout_ms}")
        solver.set("timeout", timeout_ms)

    start_t = time.perf_counter()

    try:
        check_res = solver.check()
    except Exception as exc:
        elapsed = (time.perf_counter() - start_t) * 1000.0
        result = ProofResult(
            status="error",
            verdict="inconclusive",
            solver_time_ms=elapsed,
            message=f"Solver execution failed: {exc}",
        )
        return result, result.to_evidence(requirement_id, evidence_id)

    elapsed = (time.perf_counter() - start_t) * 1000.0

    if check_res == z3.unsat:
        result = ProofResult(
            status="proved",
            verdict="pass",
            solver_time_ms=elapsed,
            message="Invariant holds universally (UNSAT under negated constraint).",
        )
    elif check_res == z3.sat:
        model = solver.model()
        counterexample: dict[str, Any] = {}
        for decl in model.decls():
            name = str(decl.name())
            try:
                if decl.arity() == 0:
                    val = model[decl]
                    counterexample[name] = str(val) if val is not None else "None"
                else:
                    counterexample[name] = f"<function/{decl.arity()}>"
            except Exception as err:
                counterexample[name] = f"<evaluation error: {err}>"

        result = ProofResult(
            status="disproved",
            verdict="fail",
            solver_time_ms=elapsed,
            counterexample=counterexample,
            message="Invariant violated; counterexample model extracted.",
        )
    else:
        timeout_info = f" after {timeout_ms} ms" if timeout_ms is not None else ""
        result = ProofResult(
            status="unknown",
            verdict="inconclusive",
            solver_time_ms=elapsed,
            message=f"Solver returned UNKNOWN (undecidable or timed out{timeout_info}).",
        )

    return result, result.to_evidence(requirement_id, evidence_id)


def verify_numeric_range(  # noqa: PLR0913
    var_name: str,
    var_type: Literal["real", "int"],
    min_val: float | int | None = None,
    max_val: float | int | None = None,
    assumptions: list[Any] | None = None,
    requirement_id: str = "REQ-RANGE-001",
    evidence_id: str = "",
    timeout_ms: int | None = None,
) -> tuple[ProofResult, Evidence]:
    """Prove a numerical range invariant on a single variable.

    Encodes system assumptions (if provided) and asserts
    ``min_val <= var <= max_val`` using Z3.

    Parameters
    ----------
    var_name:
        Name of the variable (e.g. ``"probability"``, ``"latency"``).
    var_type:
        Variable domain: ``"real"`` or ``"int"``.
    min_val:
        Optional minimum bound required by the invariant.
    max_val:
        Optional maximum bound required by the invariant.
    assumptions:
        Optional list of Z3 system model assumptions or constraints.
    requirement_id:
        Target requirement ID.
    evidence_id:
        Optional evidence ID.
    timeout_ms:
        Optional solver timeout in milliseconds.
    """
    if min_val is not None and max_val is not None and min_val > max_val:
        raise ValueError(
            f"Invalid range bounds: min_val ({min_val}) cannot be greater than max_val ({max_val})"
        )

    z3 = _check_z3_available()
    solver = z3.Solver()

    if var_type == "real":
        var = z3.Real(var_name)
    else:
        var = z3.Int(var_name)

    if assumptions:
        for assumption in assumptions:
            solver.add(assumption)

    constraints = []
    if min_val is not None:
        constraints.append(var >= min_val)
    if max_val is not None:
        constraints.append(var <= max_val)

    if not constraints:
        result = ProofResult(
            status="proved",
            verdict="pass",
            solver_time_ms=0.0,
            message="Trivial invariant (no bounds specified).",
        )
        return result, result.to_evidence(requirement_id, evidence_id)

    target_invariant = z3.And(*constraints) if len(constraints) > 1 else constraints[0]
    # Assert the NEGATION of the invariant
    solver.add(z3.Not(target_invariant))

    return verify_z3_formula(solver, requirement_id, evidence_id, timeout_ms=timeout_ms)
