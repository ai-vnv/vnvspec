"""Z3 formal verification proof bridge for vnvspec.

Provides invariant checking via the Z3 SMT solver and exports typed
``Evidence(kind="formal_proof")`` results.

Example::

    from vnvspec.proofs import verify_numeric_range

    result, ev = verify_numeric_range(
        var_name="probability",
        var_type="real",
        min_val=0.0,
        max_val=1.0,
        requirement_id="REQ-001",
    )
    assert ev.kind == "formal_proof"
"""

from vnvspec.proofs.z3_bridge import (
    ProofResult,
    ProofStatus,
    verify_numeric_range,
    verify_z3_formula,
)

__all__ = [
    "ProofResult",
    "ProofStatus",
    "verify_numeric_range",
    "verify_z3_formula",
]
