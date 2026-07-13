"""External Information Governance — reusable governance requirements for agents.

This catalog reflects published governance guidance for autonomous and
semi-autonomous AI agents as of 2026-07-13.
It is a baseline, not a substitute for expert review.

External Information Governance covers how an agent bounds, sources, and records
information it obtains from outside its trusted operator boundary (retrieved
documents, tool outputs, and third-party services). Its central concern is the
trust boundary between externally sourced content and the agent's own
instructions and decisions: such content is governed as untrusted data, kept
separate from operator instructions, and admitted only from verified sources.
This directly addresses prompt- and instruction-injection risk. The requirements
are implementation-agnostic and complement, rather than replace, existing
governance frameworks (EU AI Act, NIST AI RMF, and OWASP guidance for LLM
applications).

Sources:
- https://owasp.org/www-project-top-10-for-large-language-model-applications/
- https://www.nist.gov/itl/ai-risk-management-framework
- https://artificialintelligenceact.eu/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-13
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

_OWASP_LLM = "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
_NIST_AI_RMF = "https://www.nist.gov/itl/ai-risk-management-framework"
_EU_AI_ACT = "https://artificialintelligenceact.eu/"


def external_information_governance() -> list[Requirement]:
    """Governance requirements for how an agent bounds and sources external data."""
    return [
        Requirement(
            id="CAT-AGT-INFO-001",
            statement=(
                "The agent shall treat content received from external or tool sources "
                "as untrusted data that is not executed as agent instructions."
            ),
            rationale=(
                "Content originating outside the trusted operator boundary can carry "
                "adversarial directives. Treating such content as data rather than as "
                "instructions is the primary defense against prompt and instruction "
                "injection."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "Content received from an external or tool source is processed as data "
                "and does not alter the agent's instruction set.",
                "Instructional text embedded in external or tool content is not carried "
                "out as an agent instruction.",
            ],
            source=[_OWASP_LLM, _NIST_AI_RMF, _EU_AI_ACT],
            priority="blocking",
            standards={
                "owasp_llm": ["LLM01-prompt-injection"],
                "nist_ai_rmf": ["nist-manage"],
                "eu_ai_act": ["euaia-art15"],
            },
        ),
        Requirement(
            id="CAT-AGT-INFO-002",
            statement=(
                "The agent's operator-defined system instructions shall be isolated "
                "from externally sourced content so that the content cannot modify them."
            ),
            rationale=(
                "If externally sourced content can alter the operator's system "
                "instructions, an attacker can redirect the agent's behavior. Isolating "
                "system instructions from that content preserves operator control."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Externally sourced content cannot change the agent's operator-defined "
                "system instructions.",
                "The operator-defined system instructions in effect after processing "
                "externally sourced content match those defined by the operator.",
            ],
            source=[_OWASP_LLM, _EU_AI_ACT],
            priority="blocking",
            standards={
                "owasp_llm": ["LLM01-prompt-injection"],
                "eu_ai_act": ["euaia-art15"],
                "nist_ai_rmf": ["nist-manage"],
            },
        ),
        Requirement(
            id="CAT-AGT-INFO-003",
            statement=(
                "The agent shall record the provenance of each information item it "
                "processes, distinguishing operator instructions from externally "
                "sourced content."
            ),
            rationale=(
                "Provenance that separates operator instructions from external content "
                "is a precondition for enforcing the instruction/data boundary and for "
                "post-incident analysis of what influenced the agent."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Each information item processed by the agent has a recorded provenance.",
                "The recorded provenance identifies whether an item is an operator "
                "instruction or externally sourced content.",
            ],
            source=[_NIST_AI_RMF, _EU_AI_ACT],
            priority="high",
            standards={
                "nist_ai_rmf": ["nist-map"],
                "eu_ai_act": ["euaia-art12"],
            },
        ),
        Requirement(
            id="CAT-AGT-INFO-004",
            statement=(
                "The agent shall obtain external information only from sources that "
                "appear on an explicitly defined trusted-source list."
            ),
            rationale=(
                "Restricting external information to vetted sources limits the agent's "
                "exposure to unverified or adversarial content."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "External information obtained from a source that is absent from the "
                "trusted-source list is not used in the agent's reasoning.",
            ],
            source=[_OWASP_LLM, _NIST_AI_RMF],
            priority="high",
            standards={
                "owasp_llm": ["LLM01-prompt-injection"],
                "nist_ai_rmf": ["nist-manage"],
                "eu_ai_act": ["euaia-art10"],
            },
        ),
        Requirement(
            id="CAT-AGT-INFO-005",
            statement=(
                "The agent shall verify the authenticity of an external information "
                "source before using information from that source in a decision."
            ),
            rationale=(
                "Acting on information from an unverified source allows spoofed or "
                "tampered sources to influence agent decisions."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "Information from a source whose authenticity has not been verified is "
                "not used in a decision.",
            ],
            source=[_OWASP_LLM, _NIST_AI_RMF],
            priority="high",
            standards={
                "owasp_llm": ["LLM01-prompt-injection"],
                "nist_ai_rmf": ["nist-measure"],
                "eu_ai_act": ["euaia-art15"],
            },
        ),
        Requirement(
            id="CAT-AGT-INFO-006",
            statement=(
                "The agent shall confirm that each external information item is within "
                "its defined freshness period before using the item in a decision."
            ),
            rationale=(
                "Stale external information can lead the agent to act on conditions "
                "that no longer hold."
            ),
            verification_method="test",
            acceptance_criteria=[
                "An external information item whose age exceeds its defined freshness "
                "period is not used in a decision.",
            ],
            source=[_NIST_AI_RMF, _EU_AI_ACT],
            priority="high",
            standards={
                "nist_ai_rmf": ["nist-measure"],
                "eu_ai_act": ["euaia-art10"],
            },
        ),
        Requirement(
            id="CAT-AGT-INFO-007",
            statement=(
                "The agent shall handle conflicting external information about the same "
                "fact according to a documented governance policy before that "
                "information influences a decision."
            ),
            rationale=(
                "Different trusted sources can report conflicting information for the "
                "same fact. Requiring that such conflicts be handled under a documented "
                "governance policy keeps unresolved external disagreement from silently "
                "or arbitrarily driving agent decisions. The policy defines how conflicts "
                "are handled; this requirement governs only that such a policy exists and "
                "is applied."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A documented governance policy defines how conflicting external "
                "information about the same fact is handled.",
                "Conflicting external information about the same fact is not used in a "
                "decision except as handled under that documented governance policy.",
            ],
            source=[_NIST_AI_RMF, _EU_AI_ACT],
            priority="medium",
            standards={
                "nist_ai_rmf": ["nist-govern"],
                "eu_ai_act": ["euaia-art15"],
            },
        ),
    ]
