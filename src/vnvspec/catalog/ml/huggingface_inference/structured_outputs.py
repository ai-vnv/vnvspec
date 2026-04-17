"""HuggingFace structured output best practices.

This catalog reflects published best practices for HuggingFace Transformers
as of 2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://huggingface.co/docs/transformers/generation_strategies
- https://huggingface.co/docs/transformers/index

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: transformers>=4.40,<6.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "transformers>=4.40,<6.0"


def structured_outputs() -> list[Requirement]:
    """HuggingFace structured output requirements."""
    return [
        Requirement(
            id="CAT-HGF-STRUCT-001",
            statement=(
                "When the model is expected to produce JSON output, the "
                "generation pipeline shall validate that the raw output "
                "parses as valid JSON before returning it to the caller."
            ),
            rationale=(
                "LLMs frequently produce almost-valid JSON (trailing commas, "
                "unquoted keys, truncated output). Validation at the generation "
                "boundary prevents downstream parse failures."
            ),
            verification_method="test",
            acceptance_criteria=[
                "json.loads(output) succeeds for all structured output responses.",
                "Parse failures raise a documented error with the raw string preserved.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="blocking",
            standards={"iso_25010": ["4.1.2", "4.5.1"]},
        ),
        Requirement(
            id="CAT-HGF-STRUCT-002",
            statement=(
                "Structured output parsing errors shall preserve the raw "
                "model output string in the error object for debugging."
            ),
            rationale=(
                "Discarding the raw output on parse failure makes debugging "
                "impossible. The raw string is the primary diagnostic artifact."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The error object contains the raw output string.",
                "The error message includes the parse failure reason.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="high",
            standards={"iso_25010": ["4.7.3"]},
        ),
        Requirement(
            id="CAT-HGF-STRUCT-003",
            statement=(
                "When using constrained decoding (outlines, instructor, or "
                "similar libraries), the schema shall be validated at pipeline "
                "construction time, not at generation time."
            ),
            rationale=(
                "Schema validation at generation time wastes compute on the "
                "forward pass before failing. Early validation catches schema "
                "errors before any GPU resources are consumed."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Invalid schemas raise an error during pipeline construction.",
                "Valid schemas pass construction and produce conforming output.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="high",
        ),
        Requirement(
            id="CAT-HGF-STRUCT-004",
            statement=(
                "The structured output pipeline shall implement a retry "
                "mechanism with a configurable maximum retry count for "
                "generation attempts that fail schema validation."
            ),
            rationale=(
                "Even with constrained decoding, edge cases (max_new_tokens "
                "truncation, rare token sequences) can produce schema-invalid "
                "output. A retry mechanism improves reliability."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Failed schema validations trigger a retry up to max_retries.",
                "All retries exhausted raises a clear error.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="medium",
            standards={"iso_25010": ["4.5.3"]},
        ),
        Requirement(
            id="CAT-HGF-STRUCT-005",
            statement=(
                "The structured output pipeline shall log the schema conformance "
                "rate (successful parses / total attempts) for monitoring."
            ),
            rationale=(
                "Schema conformance rate is the primary quality metric for "
                "structured output systems. Degradation signals model drift, "
                "prompt regression, or schema incompatibility."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Conformance rate is logged or exposed as a metric.",
            ],
            source=["https://huggingface.co/docs/transformers/generation_strategies"],
            priority="medium",
        ),
        Requirement(
            id="CAT-HGF-STRUCT-006",
            statement=(
                "The structured output schema shall specify required fields "
                "explicitly and shall not rely on the model's tendency to "
                "include optional fields."
            ),
            rationale=(
                "Models may omit optional fields unpredictably. Required fields "
                "must be enforced by the schema, not assumed from model behavior."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "All fields that downstream code depends on are marked as required "
                "in the schema definition.",
            ],
            source=["https://huggingface.co/docs/transformers/index"],
            priority="high",
        ),
    ]
