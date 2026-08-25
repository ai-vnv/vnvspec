"""Tool Governance — reusable governance requirements for agentic AI tool use.

This catalog reflects published governance guidance for autonomous and
semi-autonomous AI agents as of 2026-07-13.
It is a baseline, not a substitute for expert review.

Tool Governance covers which actions an agent may take through tools, and how
high-consequence actions are authorized, gated, validated, and recorded. The
requirements are implementation-agnostic and complement, rather than replace,
existing governance frameworks (EU AI Act, NIST AI RMF, GDPR, and OWASP
guidance for LLM applications).

Sources:
- https://owasp.org/www-project-top-10-for-large-language-model-applications/
- https://www.nist.gov/itl/ai-risk-management-framework
- https://artificialintelligenceact.eu/
- https://gdpr-info.eu/art-5-gdpr/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-13
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

_OWASP_LLM = "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
_NIST_AI_RMF = "https://www.nist.gov/itl/ai-risk-management-framework"
_EU_AI_ACT = "https://artificialintelligenceact.eu/"
_GDPR_ART5 = "https://gdpr-info.eu/art-5-gdpr/"


def tool_governance() -> list[Requirement]:
    """Governance requirements for how an agent invokes tools and takes actions."""
    return [
        Requirement(
            id="CAT-AGT-TOOL-001",
            statement=(
                "The agent shall invoke only tools that appear on an explicitly "
                "defined authorization allowlist."
            ),
            rationale=(
                "A default-deny allowlist bounds the agent's action surface. "
                "Ad-hoc tool exposure is a leading cause of unintended agent actions."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A tool that is absent from the authorization allowlist is not invoked.",
            ],
            source=[_OWASP_LLM, _NIST_AI_RMF],
            priority="blocking",
            standards={
                "owasp_llm": ["LLM06-excessive-agency"],
                "nist_ai_rmf": ["nist-manage"],
                "eu_ai_act": ["euaia-art9"],
            },
        ),
        Requirement(
            id="CAT-AGT-TOOL-002",
            statement=(
                "The agent shall obtain recorded human approval before executing a "
                "tool action that has irreversible external effects."
            ),
            rationale=(
                "Irreversible actions such as payments, message dispatch, or data "
                "deletion cannot be undone. Gating them on human approval bounds "
                "worst-case harm."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "A tool action with irreversible external effects does not execute "
                "without a recorded human approval.",
                "The approval decision, the approver, and the action are recorded.",
            ],
            source=[_EU_AI_ACT, _OWASP_LLM],
            priority="blocking",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "owasp_llm": ["LLM06-excessive-agency"],
                "nist_ai_rmf": ["nist-manage"],
            },
        ),
        Requirement(
            id="CAT-AGT-TOOL-003",
            statement=(
                "The agent shall validate each tool output against the tool's declared "
                "output schema before using that output in subsequent reasoning."
            ),
            rationale=(
                "Unvalidated tool outputs can carry malformed data or injected "
                "instructions that corrupt downstream reasoning."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A tool output that does not conform to the declared output schema is "
                "rejected before use in subsequent reasoning.",
            ],
            source=[_OWASP_LLM, _NIST_AI_RMF],
            priority="high",
            standards={
                "owasp_llm": ["LLM05-improper-output-handling"],
                "nist_ai_rmf": ["nist-measure"],
            },
        ),
        Requirement(
            id="CAT-AGT-TOOL-004",
            statement=(
                "The system shall record each tool invocation with its inputs, outputs, "
                "and initiating context."
            ),
            rationale=(
                "A durable record of the actions an agent took is required for "
                "accountability and incident review."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Each tool invocation produces a record containing its inputs, "
                "outputs, and initiating context.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF, _GDPR_ART5],
            priority="high",
            standards={
                "eu_ai_act": ["euaia-art12"],
                "nist_ai_rmf": ["nist-govern"],
                "gdpr": ["art5-2"],
            },
        ),
        Requirement(
            id="CAT-AGT-TOOL-005",
            statement=(
                "The agent shall restrict each authorized tool to the operations "
                "declared in that tool's authorization entry."
            ),
            rationale=(
                "Confining each tool to its declared operations prevents a single "
                "over-scoped tool from broadening the agent's effective authority."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A tool operation that is not declared in the tool's authorization "
                "entry is not performed.",
            ],
            source=[_OWASP_LLM, _NIST_AI_RMF],
            priority="high",
            standards={
                "owasp_llm": ["LLM06-excessive-agency"],
                "nist_ai_rmf": ["nist-manage"],
            },
        ),
    ]
