# Z3 Formal Verification Proof Bridge

The `vnvspec.proofs` module bridges `vnvspec` specifications with the **Z3 SMT Solver** (`z3-solver`), enabling formal invariant verification and structured `Evidence(kind="formal_proof")` generation.

## Overview

While empirical testing demonstrates the presence of bugs under specific inputs, formal verification proves that requirements hold universally under all valid system states. The Z3 proof bridge encodes system constraints into logical formulas, submits them to Z3, and converts the solver's output into `vnvspec` evidence.

## Installation

Install `z3-solver` via optional extras:

```bash
pip install vnvspec[z3]
# or
pip install z3-solver
```

## Quick Start

```python
from vnvspec.proofs import verify_numeric_range, verify_z3_formula
import z3

# 1. Prove a numerical range invariant (0.0 <= probability <= 1.0)
proof_result, evidence = verify_numeric_range(
    var_name="probability",
    var_type="real",
    min_val=0.0,
    max_val=1.0,
    requirement_id="REQ-PROB-001",
)

assert evidence.kind == "formal_proof"
assert evidence.verdict == "pass"

# 2. Custom Z3 solver verification with counterexample extraction
solver = z3.Solver()
speed = z3.Real("speed")
solver.add(speed == 120.0)         # System assumption
solver.add(z3.Not(speed <= 100.0)) # Negated invariant requirement

result, ev = verify_z3_formula(solver, requirement_id="REQ-SPEED-001")
print(result.status)          # "disproved"
print(ev.verdict)             # "fail"
print(result.counterexample)  # {'speed': '120'}
```

## Evidence Conversion

`ProofResult` objects convert directly into `Evidence` objects via `result.to_evidence(requirement_id)`:

- `proved` $\rightarrow$ `verdict="pass"`
- `disproved` $\rightarrow$ `verdict="fail"` (with counterexample dictionary)
- `unknown` / `error` $\rightarrow$ `verdict="inconclusive"`
