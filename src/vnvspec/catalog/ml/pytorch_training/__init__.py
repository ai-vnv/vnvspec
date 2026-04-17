"""PyTorch training-loop best-practices catalog.

This catalog reflects published best practices for PyTorch as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://docs.pytorch.org/docs/stable/notes/randomness.html
- https://karpathy.github.io/2019/04/25/recipe/
- https://doi.org/10.1109/WACV.2017.58
- https://docs.pytorch.org/docs/stable/data.html

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: torch>=2.3,<3.0
Last reviewed: 2026-04-17
"""

from vnvspec.catalog.ml.pytorch_training.checkpointing import checkpointing
from vnvspec.catalog.ml.pytorch_training.data_loading import data_loading
from vnvspec.catalog.ml.pytorch_training.gradient_health import gradient_health
from vnvspec.catalog.ml.pytorch_training.loss_validation import loss_validation
from vnvspec.catalog.ml.pytorch_training.reproducibility import reproducibility

__compatible_with__ = "torch>=2.3,<3.0"

__all__ = [
    "checkpointing",
    "data_loading",
    "gradient_health",
    "loss_validation",
    "reproducibility",
]
