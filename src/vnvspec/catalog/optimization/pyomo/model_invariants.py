"""Pyomo model invariants best practices.

This catalog reflects published best practices for Pyomo as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://pyomo.readthedocs.io/en/stable/
- Hart et al., "Pyomo — Optimization Modeling in Python" (Springer, 3rd ed.)
- Williams, "Model Building in Mathematical Programming" (Wiley, 5th ed.)

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: pyomo>=6.7,<7.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "pyomo>=6.7,<7.0"


def model_invariants() -> list[Requirement]:
    """Pyomo model construction invariants."""
    return [
        Requirement(
            id="CAT-PYO-INV-001",
            statement=(
                "Every Var component shall have explicit bounds (lower and/or "
                "upper) or shall document why unbounded variables are acceptable."
            ),
            rationale=(
                "Unbounded variables can cause the solver to return unbounded "
                "solutions or very large values that are numerically unstable. "
                "Explicit bounds improve solver performance and solution quality."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Every Var has bounds set or has a documented rationale for being unbounded.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
            standards={"iso_25010": ["4.1.2"]},
        ),
        Requirement(
            id="CAT-PYO-INV-002",
            statement=(
                "The Objective component shall have an explicit sense attribute "
                "(minimize or maximize), not relying on the default."
            ),
            rationale=(
                "The default objective sense (minimize) may not match the modeler's "
                "intent. Explicit sense prevents sign-error bugs that produce "
                "worst-case instead of best-case solutions."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Every Objective has sense=minimize or sense=maximize set explicitly.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="blocking",
            standards={"do_178c": ["6.1"], "nasa_se_handbook": ["5.3"]},
        ),
        Requirement(
            id="CAT-PYO-INV-003",
            statement=(
                "Parameters shall use Param components, not Var components, "
                "for values that are fixed inputs to the model."
            ),
            rationale=(
                "Using Var for fixed parameters allows the solver to change them, "
                "producing meaningless solutions. Param enforces that the value is "
                "an input, not a decision variable."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Fixed input values are modeled as Param, not Var.",
                "No Var component has its value fixed before solving (unless "
                "intentionally fixing a decision variable).",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="blocking",
            standards={"do_178c": ["6.1"]},
        ),
        Requirement(
            id="CAT-PYO-INV-004",
            statement=(
                "Constraint expressions shall be dimensionally consistent: "
                "left-hand side and right-hand side shall have the same units "
                "or the model shall use Pyomo's units framework."
            ),
            rationale=(
                "Dimensional inconsistency in constraints is a modeling error that "
                "produces nonsensical solutions. Pyomo's units framework can catch "
                "these at construction time."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Constraint expressions have consistent units.",
                "Pyomo units framework is used, or dimensional consistency is "
                "verified by code review.",
            ],
            source=[
                "https://pyomo.readthedocs.io/en/stable/",
            ],
            priority="high",
            standards={"ieee_754": ["5.3"], "iso_25010": ["4.1.2"]},
        ),
        Requirement(
            id="CAT-PYO-INV-005",
            statement=(
                "The model shall be tested with a known-solution instance where "
                "the optimal objective value and variable values are known "
                "analytically or from a reference implementation."
            ),
            rationale=(
                "A known-solution test catches modeling errors (wrong signs, "
                "missing constraints, incorrect coefficients) that are invisible "
                "to structural validation."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A test case with known optimal solution exists.",
                "The solver's solution matches the known solution within tolerance.",
            ],
            source=[
                "https://pyomo.readthedocs.io/en/stable/",
            ],
            priority="blocking",
            standards={
                "do_178c": ["6.1", "6.3"],
                "nasa_se_handbook": ["5.4"],
                "sae_j3131": ["10.1"],
            },
        ),
        Requirement(
            id="CAT-PYO-INV-006",
            statement=(
                "The model shall log the number of variables, constraints, and "
                "nonzero coefficients before solving to track model complexity."
            ),
            rationale=(
                "Model size is the primary predictor of solve time. Logging "
                "model statistics enables early detection of model growth issues "
                "and helps estimate solve time."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Model statistics (variables, constraints, nonzeros) are logged "
                "before each solve call.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="medium",
            standards={"incose_se_handbook": ["5.7"]},
        ),
    ]
