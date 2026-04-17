"""PyTorch checkpointing best practices.

This catalog reflects published best practices for PyTorch as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://docs.pytorch.org/docs/stable/notes/serialization.html
- https://karpathy.github.io/2019/04/25/recipe/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: torch>=2.3,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "torch>=2.3,<3.0"


def checkpointing() -> list[Requirement]:
    """PyTorch checkpointing requirements."""
    return [
        Requirement(
            id="CAT-PYT-CHKPT-001",
            statement=(
                "Each checkpoint shall save the model state_dict, optimizer state_dict, "
                "learning rate scheduler state_dict, the current epoch or step count, "
                "and the random seed."
            ),
            rationale=(
                "Incomplete checkpoints prevent exact training resumption. Missing "
                "optimizer state causes a warm-restart effect that changes training dynamics."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A saved checkpoint file contains keys for model, optimizer, scheduler, "
                "step, and seed.",
                "Loading the checkpoint and resuming training produces identical loss "
                "to continuous training.",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/notes/serialization.html",
                "https://karpathy.github.io/2019/04/25/recipe/",
            ],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.7"],
                "nasa_se_handbook": ["6.5"],
                "sae_arp4754a": ["8"],
            },
        ),
        Requirement(
            id="CAT-PYT-CHKPT-002",
            statement=(
                "Checkpoints shall be saved using torch.save with "
                "_use_new_zipfile_serialization=True for forward compatibility."
            ),
            rationale=(
                "The new zipfile serialization format is the default since PyTorch 1.6 "
                "and enables more efficient loading and cross-version compatibility."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Checkpoint files are valid ZIP archives.",
                "Checkpoints can be loaded with torch.load on the same major version.",
            ],
            source=["https://docs.pytorch.org/docs/stable/notes/serialization.html"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-CHKPT-003",
            statement=(
                "The training script shall save checkpoints at regular intervals "
                "(configurable) and shall retain the best-performing checkpoint "
                "based on validation loss or the primary evaluation metric."
            ),
            rationale=(
                "Training crashes happen. Without periodic checkpointing, all progress "
                "since the last save is lost. Retaining the best checkpoint prevents "
                "overfitting from destroying the best model."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Checkpoint save interval is configurable.",
                "A 'best' checkpoint is maintained based on a named metric.",
                "At least two checkpoints exist after training: 'latest' and 'best'.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="high",
        ),
        Requirement(
            id="CAT-PYT-CHKPT-004",
            statement=(
                "The checkpoint save path shall include the experiment name, "
                "step or epoch number, and the primary metric value."
            ),
            rationale=(
                "Unnamed checkpoints accumulate in the filesystem and become "
                "impossible to identify without loading. Structured naming enables "
                "manual inspection and automated cleanup."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Checkpoint filenames follow a pattern like '{experiment}_{step}_{metric}.pt'.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-CHKPT-005",
            statement=(
                "When using HuggingFace models, checkpoints shall include "
                "the tokenizer state and any preprocessor configuration "
                "alongside the model weights."
            ),
            rationale=(
                "A model checkpoint without the matching tokenizer is unusable "
                "for inference. Tokenizer versions must be pinned to the model."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Checkpoint directory contains tokenizer config files.",
                "Loading the checkpoint restores both model and tokenizer.",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/notes/serialization.html",
            ],
            priority="high",
        ),
        Requirement(
            id="CAT-PYT-CHKPT-006",
            statement=(
                "The training script shall verify checkpoint integrity after saving "
                "by loading the checkpoint and comparing a sample prediction."
            ),
            rationale=(
                "Corrupted checkpoints from interrupted writes, disk errors, or "
                "serialization bugs are silent until inference time. Verification "
                "at save time catches corruption early."
            ),
            verification_method="test",
            acceptance_criteria=[
                "After saving, the checkpoint is loaded and a forward pass produces "
                "identical output to the in-memory model.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="medium",
            standards={
                "nist_ai_rmf": ["MS-2.7"],
                "iso_25010": ["4.6.2"],
                "nasa_se_handbook": ["5.3"],
            },
        ),
    ]
