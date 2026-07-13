"""Human Oversight — reusable governance requirements for human control of agents.

This catalog reflects published governance guidance for autonomous and
semi-autonomous AI agents as of 2026-07-13.
It is a baseline, not a substitute for expert review.

Human Oversight covers the points of effective, meaningful human control over an
agent's behavior: halting or terminating execution, approval of high-impact
actions, escalation of decisions that meet a defined oversight condition,
override of agent decisions, accountability for human intervention, operator
visibility, and preservation of human authority over the agent. The requirements
are implementation-agnostic and complement, rather than replace, existing
governance frameworks (EU AI Act and NIST AI RMF).

Sources:
- https://artificialintelligenceact.eu/
- https://www.nist.gov/itl/ai-risk-management-framework

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-13
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

_EU_AI_ACT = "https://artificialintelligenceact.eu/"
_NIST_AI_RMF = "https://www.nist.gov/itl/ai-risk-management-framework"


def human_oversight() -> list[Requirement]:
    """Governance requirements for human control over an agent's decisions."""
    return [
        Requirement(
            id="CAT-AGT-HUM-001",
            statement=(
                "The agent shall obtain human approval of an action classified as "
                "high-impact before executing that action."
            ),
            rationale=(
                "Affirmative human approval before a high-impact action gives a person "
                "the authority to stop harmful behavior that automated checks miss. It "
                "governs high-impact actions at the decision level, complementing the "
                "tool-level approval gate in Tool Governance."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "An action classified as high-impact is not executed until a human has "
                "approved it.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="blocking",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-002",
            statement=(
                "The system shall allow an authorized human to override or reverse an "
                "agent decision at a defined oversight point."
            ),
            rationale=(
                "Meaningful oversight requires the ability to intervene in an agent "
                "decision, not merely to observe it."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "At a defined oversight point, an authorized human can override or "
                "reverse the agent's decision.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-003",
            statement=(
                "The agent shall escalate a decision to a human when the decision meets "
                "a defined escalation condition."
            ),
            rationale=(
                "Escalating decisions that meet a defined escalation condition — such as "
                "low confidence, high uncertainty, or an action outside the agent's "
                "authorized scope — keeps a human in control of the cases the agent is "
                "least equipped to handle alone. The condition is defined by governance; "
                "this requirement governs only that escalation occurs when it is met."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A decision that meets the defined escalation condition is routed to a "
                "human rather than executed autonomously.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "nist_ai_rmf": ["nist-manage"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-004",
            statement=(
                "The system shall assign each agent deployment to a named human who is "
                "responsible for its oversight."
            ),
            rationale=(
                "Assigning a named responsible human prevents oversight gaps in which "
                "no person is accountable for the agent's behavior."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Each agent deployment has a named human recorded as responsible for "
                "its oversight.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="medium",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-005",
            statement=(
                "The agent shall make available to the human operator the inputs and "
                "rationale on which each decision was based."
            ),
            rationale=(
                "Operator visibility into the basis of a decision is a precondition "
                "for meaningful human oversight and for informed intervention."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "For each decision the agent makes, the human operator can view the "
                "inputs and rationale on which the decision was based.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "eu_ai_act": ["euaia-art13"],
                "nist_ai_rmf": ["nist-measure"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-006",
            statement=(
                "The system shall enable an authorized human to halt or terminate the "
                "agent's execution before the agent proceeds to its next action."
            ),
            rationale=(
                "Effective human oversight requires the authority to stop the agent "
                "before its next action. Without a halt-or-terminate capability, "
                "oversight cannot prevent imminent harm once autonomous execution has "
                "begun."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "An authorized human can halt or terminate the agent's execution before "
                "the agent proceeds to its next action.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="blocking",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-007",
            statement=(
                "The agent shall not disable or circumvent the human oversight controls "
                "defined for it."
            ),
            rationale=(
                "Human authority over the agent is preserved only if the agent cannot "
                "switch off or bypass its own oversight controls. This constraint keeps "
                "the halt, approval, escalation, and override authorities effective."
            ),
            verification_method="test",
            acceptance_criteria=[
                "The agent cannot disable the human oversight controls defined for it.",
                "The agent cannot bypass the human oversight controls defined for it.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="blocking",
            standards={
                "eu_ai_act": ["euaia-art14"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-HUM-008",
            statement=(
                "The system shall record each human oversight intervention together "
                "with the human who performed it and the affected agent action."
            ),
            rationale=(
                "A durable record of who intervened and what they changed makes human "
                "oversight and override decisions accountable and supports incident "
                "review."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Each human oversight intervention produces a record identifying the "
                "human who performed it and the affected agent action.",
            ],
            source=[_EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "eu_ai_act": ["euaia-art12"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
    ]
