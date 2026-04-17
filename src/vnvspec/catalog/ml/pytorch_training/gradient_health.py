"""PyTorch gradient health best practices.

This catalog reflects published best practices for PyTorch as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://karpathy.github.io/2019/04/25/recipe/
- https://docs.pytorch.org/docs/stable/nn.html#torch.nn.utils.clip_grad_norm_

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: torch>=2.3,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "torch>=2.3,<3.0"


def gradient_health() -> list[Requirement]:
    """PyTorch gradient health monitoring requirements."""
    return [
        Requirement(
            id="CAT-PYT-GRAD-001",
            statement=(
                "The training loop shall log the gradient L2 norm per step for "
                "at least the first and last layer of the network."
            ),
            rationale=(
                "Monitoring gradient norms is the primary tool for detecting "
                "vanishing and exploding gradients early in training."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Training logs contain gradient norm values for every step.",
                "Gradient norms are finite and non-negative.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.3"],
                "ieee_754": ["7.4", "7.5"],
                "incose_se_handbook": ["5.7"],
            },
        ),
        Requirement(
            id="CAT-PYT-GRAD-002",
            statement=(
                "The training loop shall detect NaN or Inf values in gradients "
                "and shall halt or skip the update step when detected."
            ),
            rationale=(
                "NaN/Inf gradients corrupt model weights and propagate silently. "
                "Early detection prevents wasted compute on a corrupted model."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A synthetic NaN injection into gradients triggers the detection mechanism.",
                "The model weights are not updated when NaN/Inf gradients are detected.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.3"],
                "ieee_754": ["5.7", "6.1", "6.2"],
                "iso_25010": ["4.5.1"],
            },
        ),
        Requirement(
            id="CAT-PYT-GRAD-003",
            statement=(
                "The training loop shall apply gradient clipping when the ratio "
                "of gradient norm to parameter norm exceeds a configurable threshold."
            ),
            rationale=(
                "Gradient clipping prevents exploding gradients from destabilizing "
                "training. The threshold should be documented and tunable."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Gradient clipping is applied via torch.nn.utils.clip_grad_norm_ "
                "or torch.nn.utils.clip_grad_value_.",
                "The clipping threshold is configurable and documented.",
            ],
            source=[
                "https://karpathy.github.io/2019/04/25/recipe/",
                "https://docs.pytorch.org/docs/stable/nn.html#torch.nn.utils.clip_grad_norm_",
            ],
            priority="high",
        ),
        Requirement(
            id="CAT-PYT-GRAD-004",
            statement=(
                "The training configuration shall document whether gradient "
                "accumulation is in use, the accumulation step count, and the "
                "effective batch size after accumulation."
            ),
            rationale=(
                "Gradient accumulation changes the effective learning rate. "
                "Undocumented accumulation is a common source of training bugs."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Training config specifies accumulation_steps (default 1).",
                "effective_batch_size = batch_size * accumulation_steps is logged.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-GRAD-005",
            statement=(
                "The training script shall verify that all model parameters "
                "that are expected to be trainable have requires_grad set to True "
                "before the first optimizer step."
            ),
            rationale=(
                "Accidentally frozen parameters (requires_grad=False) are a "
                "silent training bug that produces suboptimal models."
            ),
            verification_method="test",
            acceptance_criteria=[
                "An assertion checks that the count of trainable parameters "
                "matches the expected count before training starts.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="high",
            standards={
                "nist_ai_rmf": ["MS-2.3"],
                "nasa_se_handbook": ["5.3"],
                "do_178c": ["6.1"],
            },
        ),
        Requirement(
            id="CAT-PYT-GRAD-006",
            statement=(
                "The training loop shall log the learning rate at each step "
                "when using a learning rate scheduler."
            ),
            rationale=(
                "Learning rate schedule bugs are invisible without logging. "
                "Verifying the actual LR trajectory catches misconfigured schedulers."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Training logs contain the learning rate value for every step.",
                "The logged LR trajectory matches the expected schedule shape.",
            ],
            source=[
                "https://karpathy.github.io/2019/04/25/recipe/",
                "https://doi.org/10.1109/WACV.2017.58",
            ],
            priority="medium",
            standards={"nist_ai_rmf": ["MS-2.3"]},
        ),
        Requirement(
            id="CAT-PYT-GRAD-007",
            statement=(
                "The training loop shall detect floating-point overflow (gradient norm "
                "exceeding torch.finfo(dtype).max) and underflow (gradient norm below "
                "torch.finfo(dtype).tiny) conditions and shall log them as distinct events."
            ),
            rationale=(
                "IEEE 754 defines overflow and underflow as distinct exception conditions "
                "(clauses 7.4 and 7.5). Distinguishing them in logs enables targeted "
                "debugging: overflow suggests learning rate is too high; underflow "
                "suggests vanishing gradients or excessive weight decay."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Overflow events (gradient > finfo.max) are logged with 'overflow' tag.",
                "Underflow events (gradient < finfo.tiny and > 0) are logged with 'underflow' tag.",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/generated/torch.finfo.html",
            ],
            priority="high",
            standards={
                "ieee_754": ["7.4", "7.5"],
                "nist_ai_rmf": ["MS-2.3"],
                "iso_25010": ["4.5.1"],
            },
        ),
    ]
