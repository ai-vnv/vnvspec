"""HuggingFace text generation best practices.

This catalog reflects published best practices for HuggingFace Transformers
as of 2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://huggingface.co/docs/transformers/generation_strategies

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: transformers>=4.40,<6.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "transformers>=4.40,<6.0"


def generation() -> list[Requirement]:
    """HuggingFace text generation requirements."""
    return [
        Requirement(
            id="CAT-HGF-GEN-001",
            statement=(
                "The generation configuration shall set do_sample explicitly "
                "rather than relying on the default value, and shall pair it "
                "with an explicit temperature when do_sample is True."
            ),
            rationale=(
                "The default do_sample value varies by model. Relying on the "
                "default produces inconsistent behavior across model versions. "
                "Temperature without do_sample=True has no effect."
            ),
            verification_method="test",
            acceptance_criteria=[
                "GenerationConfig has do_sample set explicitly.",
                "When do_sample=True, temperature is also set explicitly.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="blocking",
            standards={"nasa_se_handbook": ["6.5"]},
        ),
        Requirement(
            id="CAT-HGF-GEN-002",
            statement=(
                "The generation configuration shall not set both top_p and top_k "
                "to non-default values simultaneously unless the interaction is "
                "documented and intentional."
            ),
            rationale=(
                "top_p (nucleus sampling) and top_k interact in non-obvious ways. "
                "Setting both narrows the sampling distribution more than intended."
            ),
            verification_method="test",
            acceptance_criteria=[
                "At most one of top_p or top_k is set to a non-default value, "
                "or both are set with documented justification.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-GEN-003",
            statement=(
                "The generation configuration shall use max_new_tokens instead "
                "of max_length to control output length."
            ),
            rationale=(
                "max_length includes the prompt length, making the actual generation "
                "length input-dependent. max_new_tokens controls only the generated "
                "portion, which is more predictable and debuggable."
            ),
            verification_method="test",
            acceptance_criteria=[
                "GenerationConfig uses max_new_tokens, not max_length.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-GEN-004",
            statement=(
                "The generation pipeline shall configure stop tokens (eos_token_id "
                "or stopping_criteria) and shall verify that generated output "
                "terminates correctly."
            ),
            rationale=(
                "Without proper stop tokens, generation continues to max_new_tokens, "
                "producing trailing garbage. Stop token misconfiguration is a common "
                "source of malformed output."
            ),
            verification_method="test",
            acceptance_criteria=[
                "eos_token_id is set in the GenerationConfig.",
                "Generated output ends at a stop token or max_new_tokens.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="high",
            standards={"iso_25010": ["4.1.2"]},
        ),
        Requirement(
            id="CAT-HGF-GEN-005",
            statement=(
                "The generation pipeline shall decode output tokens using the "
                "same tokenizer used for encoding, with skip_special_tokens set "
                "appropriately for the use case."
            ),
            rationale=(
                "Decoding with a different tokenizer or incorrect special-token "
                "handling produces corrupted text. skip_special_tokens=True is "
                "correct for user-facing output but wrong for debugging."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Decoding uses the same tokenizer instance as encoding.",
                "skip_special_tokens is set explicitly based on the use case.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="medium",
        ),
        Requirement(
            id="CAT-HGF-GEN-006",
            statement=(
                "The generation configuration shall set a repetition_penalty or "
                "no_repeat_ngram_size when generating long-form text to prevent "
                "degenerate repetition."
            ),
            rationale=(
                "Autoregressive models are prone to repetition loops, especially "
                "with greedy or low-temperature sampling. Repetition penalties "
                "are a standard mitigation."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "GenerationConfig sets repetition_penalty > 1.0 or "
                "no_repeat_ngram_size > 0 for long-form generation tasks.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="medium",
        ),
    ]
