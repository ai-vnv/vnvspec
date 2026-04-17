"""Pyomo optimization best-practices catalog.

This catalog reflects published best practices for Pyomo as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://pyomo.readthedocs.io/en/stable/
- https://pyomo.readthedocs.io/en/stable/working_models.html
- Hart et al., "Pyomo — Optimization Modeling in Python" (Springer, 3rd ed.)

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: pyomo>=6.7,<7.0
Last reviewed: 2026-04-17
"""

from vnvspec.catalog.optimization.pyomo.constraint_validation import constraint_validation
from vnvspec.catalog.optimization.pyomo.model_invariants import model_invariants
from vnvspec.catalog.optimization.pyomo.solver_status import solver_status

__compatible_with__ = "pyomo>=6.7,<7.0"

__all__ = [
    "constraint_validation",
    "model_invariants",
    "solver_status",
]
