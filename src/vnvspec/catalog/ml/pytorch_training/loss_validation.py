"""PyTorch loss validation best practices.

This catalog reflects published best practices for PyTorch as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://karpathy.github.io/2019/04/25/recipe/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: torch>=2.3,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "torch>=2.3,<3.0"


def loss_validation() -> list[Requirement]:
    """PyTorch loss validation requirements."""
    return [
        Requirement(
            id="CAT-PYT-LOSS-001",
            statement=(
                "The first-step training loss shall match the expected value for "
                "a random (untrained) model within a documented tolerance."
            ),
            rationale=(
                "Karpathy's Recipe step 5: verify the loss at initialization. "
                "For a C-class classifier with balanced data, the expected loss "
                "is -ln(1/C). A significantly different value indicates a bug in "
                "the model, loss function, or data pipeline."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The first-step loss is within 10% of the theoretical baseline "
                "for the chosen loss function and number of classes.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.3"],
                "do_178c": ["6.1"],
                "sae_j3131": ["10.1"],
            },
        ),
        Requirement(
            id="CAT-PYT-LOSS-002",
            statement=(
                "The training loop shall verify that the loss value is finite "
                "(not NaN, not Inf) at every step."
            ),
            rationale=(
                "NaN/Inf loss values indicate numerical instability, division by zero, "
                "or corrupted inputs. Training should halt immediately rather than "
                "waste compute on a corrupted model."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A torch.isfinite() check runs on the loss at every step.",
                "Training halts with a clear error message if the loss is not finite.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="blocking",
            standards={
                "ieee_754": ["5.7", "7.1"],
                "iso_25010": ["4.5.1"],
            },
        ),
        Requirement(
            id="CAT-PYT-LOSS-003",
            statement=(
                "The training loop shall verify that the loss decreases within "
                "the first N steps on a small overfit batch."
            ),
            rationale=(
                "Karpathy's Recipe step 4: overfit a single batch first. If the "
                "model cannot drive the loss to near-zero on a tiny batch, there "
                "is a bug in the training pipeline."
            ),
            verification_method="test",
            acceptance_criteria=[
                "On a batch of 4-8 samples trained for 100 steps, the loss is "
                "below 10% of the initial value.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="blocking",
            standards={
                "nist_ai_rmf": ["MS-2.3"],
                "do_178c": ["6.1"],
                "nasa_se_handbook": ["5.3"],
            },
        ),
        Requirement(
            id="CAT-PYT-LOSS-004",
            statement=(
                "The training loop shall log both training loss and validation loss "
                "at regular intervals (at least once per epoch)."
            ),
            rationale=(
                "Training loss alone is insufficient to detect overfitting. "
                "The gap between training and validation loss is the primary "
                "signal for generalization."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Training logs contain both train_loss and val_loss entries.",
                "val_loss is logged at least once per epoch.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="high",
            standards={"nist_ai_rmf": ["MS-2.3"]},
        ),
        Requirement(
            id="CAT-PYT-LOSS-005",
            statement=(
                "The loss function shall be applied to model outputs with the "
                "correct input shape and shall not silently broadcast mismatched "
                "dimensions."
            ),
            rationale=(
                "PyTorch loss functions often broadcast silently when target and "
                "prediction shapes differ (e.g., [B, C] vs [B]). This produces "
                "incorrect gradients without any error or warning."
            ),
            verification_method="test",
            acceptance_criteria=[
                "An assertion verifies that prediction.shape and target.shape "
                "are compatible before computing the loss.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="high",
        ),
        Requirement(
            id="CAT-PYT-LOSS-006",
            statement=(
                "The training script shall implement early stopping or a maximum "
                "epoch count to prevent unbounded training."
            ),
            rationale=(
                "Training without a termination condition wastes compute and risks "
                "severe overfitting. Either early stopping (based on validation loss "
                "plateau) or a hard epoch limit should be configured."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Training config specifies max_epochs or an early stopping criterion.",
            ],
            source=["https://karpathy.github.io/2019/04/25/recipe/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-PYT-LOSS-007",
            statement=(
                "The training loop shall use numerically stable implementations of "
                "common loss functions (log-sum-exp, cross-entropy) rather than naive "
                "formulations that are prone to overflow or underflow."
            ),
            rationale=(
                "Naive implementations of log(sum(exp(x))) overflow for large x and "
                "underflow for negative x. PyTorch provides numerically stable "
                "alternatives (torch.logsumexp, F.cross_entropy with logits) that "
                "should always be preferred."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Loss functions use torch.nn.functional.cross_entropy (not manual "
                "softmax + log), or torch.logsumexp where applicable.",
                "Loss values remain finite for inputs in the range [-100, 100].",
            ],
            source=[
                "https://docs.pytorch.org/docs/stable/generated/torch.logsumexp.html",
                "https://karpathy.github.io/2019/04/25/recipe/",
            ],
            priority="blocking",
            standards={
                "ieee_754": ["6.1", "7.4", "7.5"],
                "nist_ai_rmf": ["MS-2.3"],
                "iso_25010": ["4.1.2"],
            },
        ),
    ]
