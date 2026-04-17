"""Pyomo solver status checking best practices.

This catalog reflects published best practices for Pyomo as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://pyomo.readthedocs.io/en/stable/
- https://pyomo.readthedocs.io/en/stable/working_models.html

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: pyomo>=6.7,<7.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "pyomo>=6.7,<7.0"


def solver_status() -> list[Requirement]:
    """Pyomo solver status checking requirements."""
    return [
        Requirement(
            id="CAT-PYO-SOLV-001",
            statement=(
                "The application shall check results.solver.termination_condition "
                "== TerminationCondition.optimal before reading any variable values "
                "from the solved model."
            ),
            rationale=(
                "Reading variable values from a non-optimal solution produces "
                "meaningless results. The solver may have returned an infeasible, "
                "unbounded, or time-limited solution."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Variable values are only accessed after confirming optimal status.",
                "Non-optimal termination conditions raise or log an error.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/working_models.html"],
            priority="blocking",
            standards={"nasa_se_handbook": ["5.3"], "do_178c": ["6.1"], "iso_25010": ["4.1.2"]},
        ),
        Requirement(
            id="CAT-PYO-SOLV-002",
            statement=(
                "The application shall handle infeasible, unbounded, and "
                "maxTimeLimit termination conditions explicitly with appropriate "
                "error messages or fallback logic."
            ),
            rationale=(
                "Each non-optimal termination condition has different implications. "
                "Infeasible means the constraints are contradictory; unbounded means "
                "the objective is unconstrained; time limit means the solver ran out "
                "of time before proving optimality."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Infeasible termination produces a clear error message.",
                "Unbounded termination produces a clear error message.",
                "Time-limited termination logs the gap and returns the best bound.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/working_models.html"],
            priority="blocking",
            standards={"iso_25010": ["4.5.3"], "sae_arp4754a": ["7"]},
        ),
        Requirement(
            id="CAT-PYO-SOLV-003",
            statement=(
                "The application shall log the solver wall-clock time, iteration "
                "count, and optimality gap for every solve call."
            ),
            rationale=(
                "Solver performance metrics are essential for debugging slow models, "
                "identifying numerical issues, and tracking model complexity growth."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Solver time, iterations, and gap are logged after every solve.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
            standards={"incose_se_handbook": ["5.7"], "iso_25010": ["4.7.3"]},
        ),
        Requirement(
            id="CAT-PYO-SOLV-004",
            statement=(
                "The solver shall be configured with an explicit time limit "
                "to prevent unbounded solve times in production."
            ),
            rationale=(
                "Without a time limit, a solver may run for hours or days on a "
                "difficult instance. Explicit time limits bound the worst-case "
                "response time."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The solver is called with a time_limit or timelimit option.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
            standards={"iso_25010": ["4.2.1"]},
        ),
        Requirement(
            id="CAT-PYO-SOLV-005",
            statement=(
                "The application shall verify that the solver is available on the "
                "deployment platform before attempting to solve."
            ),
            rationale=(
                "Pyomo supports many solvers but does not bundle them. A missing "
                "solver produces an opaque error at solve time that is hard to "
                "debug in production."
            ),
            verification_method="test",
            acceptance_criteria=[
                "SolverFactory(name).available() is checked before solve().",
                "A missing solver produces a clear error message.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="high",
            standards={"nasa_se_handbook": ["6.5"]},
        ),
        Requirement(
            id="CAT-PYO-SOLV-006",
            statement=(
                "The application shall log the solver name and version used for "
                "each solve call to support result reproducibility."
            ),
            rationale=(
                "Different solver versions may produce different optimal solutions "
                "for the same model. Logging the solver version enables reproducing "
                "and comparing results."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Solver name and version are logged with each solve result.",
            ],
            source=["https://pyomo.readthedocs.io/en/stable/"],
            priority="medium",
            standards={"nasa_se_handbook": ["6.5"], "incose_se_handbook": ["5.5"]},
        ),
    ]
