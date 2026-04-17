"""HuggingFace attention mask best practices.

This catalog reflects published best practices for HuggingFace Transformers
as of 2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://huggingface.co/docs/transformers/index
- https://arxiv.org/abs/1706.03762

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: transformers>=4.40,<6.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "transformers>=4.40,<6.0"


def attention_masks() -> list[Requirement]:
    """HuggingFace attention mask requirements."""
    return [
        Requirement(
            id="CAT-HGF-ATTN-001",
            statement=(
                "The attention mask shape shall match the input_ids shape "
                "exactly (batch_size, sequence_length)."
            ),
            rationale=(
                "Shape mismatches between input_ids and attention_mask cause "
                "silent broadcasting errors or runtime crashes depending on "
                "the model implementation."
            ),
            verification_method="test",
            acceptance_criteria=[
                "attention_mask.shape == input_ids.shape for every forward pass.",
            ],
            source=[
                "https://huggingface.co/docs/transformers/index",
                "https://arxiv.org/abs/1706.03762",
            ],
            priority="blocking",
        ),
        Requirement(
            id="CAT-HGF-ATTN-002",
            statement=(
                "Padding tokens shall be masked to 0 in the attention mask, "
                "and real tokens shall be set to 1."
            ),
            rationale=(
                "Attending to padding tokens introduces noise into the model's "
                "representations. The convention is 1 for real tokens and 0 for "
                "padding across all HuggingFace models."
            ),
            verification_method="test",
            acceptance_criteria=[
                "For every padded position, attention_mask[i] == 0.",
                "For every real token position, attention_mask[i] == 1.",
            ],
            source=["https://huggingface.co/docs/transformers/index"],
            priority="blocking",
        ),
        Requirement(
            id="CAT-HGF-ATTN-003",
            statement=(
                "For autoregressive (causal) models, the causal mask shall be "
                "applied so that each token can only attend to previous tokens "
                "and itself."
            ),
            rationale=(
                "Causal models (GPT-family) must not attend to future tokens. "
                "Missing the causal mask during inference produces outputs that "
                "are inconsistent with training."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The model's forward pass applies a causal attention mask.",
                "Token at position i does not attend to any position j > i.",
            ],
            source=["https://arxiv.org/abs/1706.03762"],
            priority="blocking",
            standards={"nist_ai_rmf": ["MS-2.3"]},
        ),
        Requirement(
            id="CAT-HGF-ATTN-004",
            statement=(
                "For left-padded inputs, position IDs shall be offset correctly "
                "so that the first real token has position ID 0."
            ),
            rationale=(
                "Left-padded inputs with incorrect position IDs cause the model "
                "to assign wrong positional embeddings, degrading output quality "
                "especially for position-sensitive architectures (RoPE, ALiBi)."
            ),
            verification_method="test",
            acceptance_criteria=[
                "For a left-padded input with P padding tokens, the first real "
                "token has position_id == 0, not P.",
            ],
            source=[
                "https://huggingface.co/docs/transformers/index",
                "https://arxiv.org/abs/1706.03762",
            ],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-ATTN-005",
            statement=(
                "The inference pipeline shall explicitly pass attention_mask to "
                "the model's forward method rather than relying on automatic "
                "mask generation."
            ),
            rationale=(
                "Automatic attention mask generation may not handle custom "
                "padding or mixed-length batches correctly. Explicit masks "
                "ensure the caller controls masking behavior."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "model.forward() or model.generate() receives an explicit attention_mask argument.",
            ],
            source=["https://huggingface.co/docs/transformers/index"],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-ATTN-006",
            statement=(
                "The attention mask shall be validated to contain only values "
                "0 and 1 before being passed to the model."
            ),
            rationale=(
                "Non-binary attention mask values (e.g., from floating-point "
                "rounding or incorrect construction) produce undefined behavior "
                "in most attention implementations."
            ),
            verification_method="test",
            acceptance_criteria=[
                "An assertion verifies that attention_mask contains only 0 and 1 values.",
            ],
            source=["https://huggingface.co/docs/transformers/index"],
            priority="medium",
        ),
    ]
