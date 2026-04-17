"""Pyomo constraint validation best practices.

This catalog reflects published best practices for Pyomo as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://pyomo.readthedocs.io/en/stable/
- Hart et al., "Pyomo — Optimization Modeling in Python" (Springer, 3rd ed.)

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: pyomo>=6.7,<7.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "pyomo>=6.7,<7.0"


def constraint_validation() -> list[Requirement]:
    """Pyomo post-solve constraint validation requirements."""
    return [
        Requirement(
            id="CAT-PYO-CVAL-001",
            statement=(
                "After solving, the application shall evaluate every constraint "
                "with the solution values and verify satisfaction within an "
                "explicit numerical tolerance."
            ),
            rationale=(
                "Solvers use floating-point arithmetic and may return solutions "
                "that violate constraints by small amounts. Post-solve validation "
                "with an explicit tolerance catches numerical issues."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All constraints are evaluated post-solve.",
                "Violations above the tolerance are reported.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="blocking",
        ),
        Requirement(
            id="CAT-PYO-CVAL-002",
            statement=(
                "The post-solve validation shall report the worst-violated "
                "constraint and its violation magnitude."
            ),
            rationale=(
                "Knowing which constraint is most violated and by how much "
                "is essential for diagnosing model formulation issues and "
                "solver numerical precision problems."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The worst-violated constraint name and violation value are logged.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
        ),
        Requirement(
            id="CAT-PYO-CVAL-003",
            statement=(
                "The constraint validation tolerance shall be configurable "
                "and shall default to a value appropriate for the solver's "
                "feasibility tolerance (typically 1e-6)."
            ),
            rationale=(
                "The validation tolerance should match or be slightly larger than "
                "the solver's feasibility tolerance. A tolerance too tight produces "
                "false violations; too loose hides real issues."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The tolerance is configurable with a documented default.",
                "The default tolerance is consistent with the solver's feasibility tolerance.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYO-CVAL-004",
            statement=(
                "The application shall validate that variable bounds are "
                "satisfied in the solution, not just constraints."
            ),
            rationale=(
                "Solvers may return solutions that violate variable bounds due to "
                "numerical precision. Bound violations are as important as "
                "constraint violations for solution correctness."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All variable values are within their declared bounds (plus tolerance).",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
        ),
        Requirement(
            id="CAT-PYO-CVAL-005",
            statement=(
                "The application shall compare the solver's reported objective "
                "value with the objective evaluated at the solution point and "
                "flag discrepancies."
            ),
            rationale=(
                "Discrepancies between the solver's reported objective and the "
                "evaluated objective indicate solver bugs, model loading issues, "
                "or floating-point drift."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The objective is re-evaluated at the solution point.",
                "A discrepancy above tolerance is flagged.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYO-CVAL-006",
            statement=(
                "For integer programming models, the application shall verify "
                "that integer variables have integer values in the solution "
                "within a small tolerance."
            ),
            rationale=(
                "MIP solvers may return near-integer values (e.g., 0.9999 instead "
                "of 1.0) due to numerical precision. Downstream code that treats "
                "these as integers may produce incorrect results."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Integer variables have values within 1e-5 of the nearest integer.",
                "Values are rounded to integers for downstream use.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
        ),
    ]
