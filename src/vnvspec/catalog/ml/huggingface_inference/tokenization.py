"""HuggingFace tokenization best practices.

This catalog reflects published best practices for HuggingFace Transformers
as of 2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://huggingface.co/docs/transformers/tokenizer_summary
- https://huggingface.co/docs/transformers/index

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: transformers>=4.40,<6.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "transformers>=4.40,<6.0"


def tokenization() -> list[Requirement]:
    """HuggingFace tokenization requirements."""
    return [
        Requirement(
            id="CAT-HGF-TOKEN-001",
            statement=(
                "The tokenizer shall produce a lossless round-trip on ASCII and "
                "common Unicode inputs: decode(encode(text)) shall equal the "
                "original text for inputs that do not contain special tokens."
            ),
            rationale=(
                "Tokenizer round-trip failures indicate encoding bugs, missing "
                "vocabulary entries, or normalization side effects that corrupt "
                "input semantics."
            ),
            verification_method="test",
            acceptance_criteria=[
                "decode(encode(text)) == text for a test suite of ASCII, Unicode, "
                "and edge-case inputs (empty string, single character, emoji).",
            ],
            source=["https://huggingface.co/docs/transformers/tokenizer_summary"],
            priority="blocking",
            standards={"iso_25010": ["4.1.2"], "do_178c": ["6.1"]},
        ),
        Requirement(
            id="CAT-HGF-TOKEN-002",
            statement=(
                "The tokenizer shall insert the correct special tokens (BOS, EOS, "
                "SEP, CLS) as defined by the model's tokenizer configuration."
            ),
            rationale=(
                "Missing or incorrect special tokens cause the model to interpret "
                "inputs incorrectly. The expected tokens vary by model architecture."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Encoded output starts with the model's BOS/CLS token (if applicable).",
                "Encoded output ends with the model's EOS/SEP token (if applicable).",
            ],
            source=["https://huggingface.co/docs/transformers/tokenizer_summary"],
            priority="blocking",
            standards={"do_178c": ["6.1"]},
        ),
        Requirement(
            id="CAT-HGF-TOKEN-003",
            statement=(
                "The tokenizer shall use an explicit max_length parameter for "
                "truncation rather than relying on the model's default max position "
                "embeddings."
            ),
            rationale=(
                "Silent truncation at the model's default max length discards input "
                "without warning. Explicit max_length forces the caller to handle "
                "long inputs intentionally."
            ),
            verification_method="test",
            acceptance_criteria=[
                "tokenizer(..., truncation=True, max_length=N) is called with an "
                "explicit max_length value.",
                "Inputs exceeding max_length produce a logged warning or error.",
            ],
            source=["https://huggingface.co/docs/transformers/tokenizer_summary"],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-TOKEN-004",
            statement=(
                "The padding side shall be set explicitly: left padding for "
                "causal (autoregressive) models, right padding for encoder models."
            ),
            rationale=(
                "Incorrect padding side causes attention to attend to padding tokens "
                "at the wrong end. Causal models require left padding so that the "
                "last token is always a real token for generation."
            ),
            verification_method="test",
            acceptance_criteria=[
                "tokenizer.padding_side is 'left' for causal models.",
                "tokenizer.padding_side is 'right' for encoder models.",
            ],
            source=[
                "https://huggingface.co/docs/transformers/tokenizer_summary",
                "https://arxiv.org/abs/1706.03762",
            ],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-TOKEN-005",
            statement=(
                "The tokenizer version shall be pinned to match the model checkpoint "
                "and shall be saved alongside the model weights."
            ),
            rationale=(
                "Tokenizer vocabulary changes between versions cause silent encoding "
                "drift. A model trained with tokenizer v1 and served with tokenizer v2 "
                "produces incorrect outputs."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "The tokenizer is loaded from the same checkpoint as the model.",
                "tokenizer.save_pretrained() is called when saving the model.",
            ],
            source=["https://huggingface.co/docs/transformers/index"],
            priority="high",
            standards={"nasa_se_handbook": ["6.5"], "incose_se_handbook": ["5.5"]},
        ),
        Requirement(
            id="CAT-HGF-TOKEN-006",
            statement=(
                "The tokenizer shall be tested with adversarial inputs including "
                "empty strings, strings of only whitespace, and strings containing "
                "only special token text."
            ),
            rationale=(
                "Edge-case tokenizer inputs expose normalization bugs and special-token "
                "handling errors that do not appear in normal text."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Tokenizing an empty string does not raise an exception.",
                "Tokenizing whitespace-only input produces a valid token sequence.",
            ],
            source=["https://huggingface.co/docs/transformers/tokenizer_summary"],
            priority="medium",
            standards={"iso_25010": ["4.5.3"]},
        ),
    ]
