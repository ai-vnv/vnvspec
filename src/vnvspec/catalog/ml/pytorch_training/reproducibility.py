"""PyTorch reproducibility best practices.

This catalog reflects published best practices for PyTorch as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://docs.pytorch.org/docs/stable/notes/randomness.html
- https://docs.pytorch.org/docs/stable/data.html

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: torch>=2.3,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "torch>=2.3,<3.0"


def reproducibility() -> list[Requirement]:
    """PyTorch reproducibility requirements."""
    return [
        Requirement(
            id="CAT-PYT-REPRO-001",
            statement=(
                "The training script shall set torch.manual_seed, numpy.random.seed, "
                "random.seed, and the PYTHONHASHSEED environment variable before any "
                "model or data construction."
            ),
            rationale=(
                "Reproducibility requires seeding all RNGs that influence model "
                "initialization, data ordering, or hash-based operations."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Two consecutive runs with identical seeds produce identical loss "
                "values at step 100 (tolerance: 1e-6).",
            ],
            source=["https://docs.pytorch.org/docs/stable/notes/randomness.html"],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.7"],
                "ieee_754": ["11"],
                "nasa_se_handbook": ["5.3"],
                "do_178c": ["6.3"],
            },
        ),
        Requirement(
            id="CAT-PYT-REPRO-002",
            statement=(
                "The training script shall call torch.use_deterministic_algorithms(True) "
                "or shall document the specific non-deterministic operations in use and "
                "the rationale for accepting them."
            ),
            rationale=(
                "Non-deterministic GPU operations (atomicAdd, scatter, etc.) cause "
                "run-to-run variance that may mask training bugs."
            ),
            verification_method="test",
            acceptance_criteria=[
                "torch.are_deterministic_algorithms_enabled() returns True before "
                "training starts, or the rationale is documented in the training config.",
            ],
            source=["https://docs.pytorch.org/docs/stable/notes/randomness.html"],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.7"],
                "ieee_754": ["11"],
                "iso_25010": ["4.5.4"],
            },
        ),
        Requirement(
            id="CAT-PYT-REPRO-003",
            statement=(
                "The training script shall set torch.backends.cudnn.deterministic to True "
                "and torch.backends.cudnn.benchmark to False when reproducibility is required."
            ),
            rationale=(
                "cuDNN benchmark mode selects the fastest convolution algorithm at runtime, "
                "which may differ across runs. Deterministic mode ensures consistent results."
            ),
            verification_method="test",
            acceptance_criteria=[
                "torch.backends.cudnn.deterministic is True at training start.",
                "torch.backends.cudnn.benchmark is False at training start.",
            ],
            source=["https://docs.pytorch.org/docs/stable/notes/randomness.html"],
            priority="high",
            standards={"nist_ai_rmf": ["MS-2.7"]},
        ),
        Requirement(
            id="CAT-PYT-REPRO-004",
            statement=(
                "The DataLoader shall be constructed with an explicit worker_init_fn and "
                "a generator seeded from the global seed when num_workers > 0."
            ),
            rationale=(
                "Worker processes inherit the parent RNG state by default. Without an "
                "explicit worker_init_fn, each worker produces the same random sequence, "
                "reducing data augmentation effectiveness and harming reproducibility."
            ),
            verification_method="test",
            acceptance_criteria=[
                "DataLoader.worker_init_fn is not None when num_workers > 0.",
                "DataLoader.generator is set to a seeded torch.Generator.",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/notes/randomness.html",
                "https://docs.pytorch.org/docs/stable/data.html",
            ],
            priority="high",
            standards={"nist_ai_rmf": ["MS-2.7"]},
        ),
        Requirement(
            id="CAT-PYT-REPRO-005",
            statement=(
                "The training script shall set the CUBLAS_WORKSPACE_CONFIG environment "
                "variable to ':4096:8' or ':16:8' when running on CUDA >= 10.2."
            ),
            rationale=(
                "cuBLAS workspace selection is non-deterministic unless this environment "
                "variable is set, which can cause run-to-run variance in matrix operations."
            ),
            verification_method="test",
            acceptance_criteria=[
                "os.environ['CUBLAS_WORKSPACE_CONFIG'] is set to ':4096:8' or ':16:8' "
                "before any CUDA operations.",
            ],
            source=["https://docs.pytorch.org/docs/stable/notes/randomness.html"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-REPRO-006",
            statement=(
                "The training configuration shall record the exact software versions "
                "(torch, CUDA, cuDNN, Python) used for each training run."
            ),
            rationale=(
                "Reproducibility across environments requires knowing the exact software "
                "stack. Version mismatches are the most common cause of non-reproducibility."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Training logs include torch.__version__, torch.version.cuda, "
                "torch.backends.cudnn.version(), and sys.version.",
            ],
            source=["https://docs.pytorch.org/docs/stable/notes/randomness.html"],
            priority="medium",
            standards={
                "nist_ai_rmf": ["MS-2.7"],
                "nasa_se_handbook": ["6.5"],
                "incose_se_handbook": ["5.5"],
            },
        ),
    ]
