"""HuggingFace inference best-practices catalog.

This catalog reflects published best practices for HuggingFace Transformers
as of 2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://huggingface.co/docs/transformers/index
- https://huggingface.co/docs/transformers/generation_strategies
- https://huggingface.co/docs/transformers/tokenizer_summary
- https://arxiv.org/abs/1706.03762

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: transformers>=4.40,<6.0
Last reviewed: 2026-04-17
"""

from vnvspec.catalog.ml.huggingface_inference.attention_masks import attention_masks
from vnvspec.catalog.ml.huggingface_inference.generation import generation
from vnvspec.catalog.ml.huggingface_inference.structured_outputs import structured_outputs
from vnvspec.catalog.ml.huggingface_inference.tokenization import tokenization

__compatible_with__ = "transformers>=4.40,<6.0"

__all__ = [
    "attention_masks",
    "generation",
    "structured_outputs",
    "tokenization",
]
