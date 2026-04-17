"""PyTorch data loading best practices.

This catalog reflects published best practices for PyTorch as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://docs.pytorch.org/docs/stable/data.html
- https://docs.pytorch.org/docs/stable/notes/randomness.html

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: torch>=2.3,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "torch>=2.3,<3.0"


def data_loading() -> list[Requirement]:
    """PyTorch data loading requirements."""
    return [
        Requirement(
            id="CAT-PYT-DATA-001",
            statement=(
                "The DataLoader shall use num_workers > 0 only when an explicit "
                "worker_init_fn is provided to seed each worker's RNG."
            ),
            rationale=(
                "Without worker_init_fn, all workers share the same RNG state, "
                "producing identical random augmentations and undermining data "
                "diversity within each batch."
            ),
            verification_method="test",
            acceptance_criteria=[
                "DataLoader with num_workers > 0 has worker_init_fn set.",
                "Each worker produces different random augmentations.",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/data.html",
                "https://docs.pytorch.org/docs/stable/notes/randomness.html",
            ],
            priority="blocking",
            standards={"nist_ai_rmf": ["MS-2.7"]},
        ),
        Requirement(
            id="CAT-PYT-DATA-002",
            statement=(
                "The DataLoader shall set pin_memory=True only when training on CUDA devices."
            ),
            rationale=(
                "pin_memory accelerates CPU-to-GPU data transfer by using "
                "page-locked memory. On CPU-only training it wastes memory "
                "and can cause OOM errors."
            ),
            verification_method="test",
            acceptance_criteria=[
                "pin_memory is True only when torch.cuda.is_available() is True.",
            ],
            source=["https://docs.pytorch.org/docs/stable/data.html"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-DATA-003",
            statement=(
                "The DataLoader configuration shall document the persistent_workers "
                "setting and its interaction with num_workers."
            ),
            rationale=(
                "persistent_workers=True keeps worker processes alive between epochs, "
                "reducing startup overhead but increasing memory usage. The trade-off "
                "should be explicitly documented."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Training config specifies persistent_workers explicitly.",
                "Memory impact of persistent_workers is documented.",
            ],
            source=["https://docs.pytorch.org/docs/stable/data.html"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-DATA-004",
            statement=(
                "The training script shall verify that the dataset produces "
                "identical samples in the same order when given the same seed "
                "across two independent runs."
            ),
            rationale=(
                "Dataset reproducibility is a prerequisite for training reproducibility. "
                "Random augmentations, shuffling, and sampling must all be seeded."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Two independent DataLoader iterations with the same seed produce "
                "identical first-batch samples (bit-exact for tensors).",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/notes/randomness.html",
            ],
            priority="high",
            standards={
                "nist_ai_rmf": ["MS-2.7"],
                "ieee_754": ["11"],
                "do_178c": ["6.3"],
            },
        ),
        Requirement(
            id="CAT-PYT-DATA-005",
            statement=(
                "The training script shall log the total number of training samples, "
                "validation samples, and the effective batch size at the start of training."
            ),
            rationale=(
                "Dataset size mismatches between expected and actual are a common "
                "source of training bugs. Logging the counts enables quick sanity checks."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Training logs include len(train_dataset), len(val_dataset), "
                "and effective_batch_size before the first training step.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="high",
            standards={
                "incose_se_handbook": ["5.7"],
            },
        ),
        Requirement(
            id="CAT-PYT-DATA-006",
            statement=(
                "The DataLoader shall use drop_last=True for training batches "
                "when batch normalization is used, or shall document the rationale "
                "for keeping partial batches."
            ),
            rationale=(
                "Partial final batches with batch normalization produce unreliable "
                "statistics, especially when the partial batch is very small. "
                "drop_last=True avoids this at the cost of discarding a few samples."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Training DataLoader has drop_last=True when the model uses "
                "BatchNorm layers, or the rationale for keeping partial batches "
                "is documented.",
            ],
            source=["https://docs.pytorch.org/docs/stable/data.html"],
            priority="medium",
        ),
    ]
