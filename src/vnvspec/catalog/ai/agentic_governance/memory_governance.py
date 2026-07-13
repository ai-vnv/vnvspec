"""Memory Governance — reusable governance requirements for agent memory.

This catalog reflects published governance guidance for autonomous and
semi-autonomous AI agents as of 2026-07-13.
It is a baseline, not a substitute for expert review.

Memory Governance covers how an agent's persisted memory is bounded and
controlled: the scope of what may be retained, isolation between users or
tenants, authorization of persistence and retrieval, retention limits, deletion
on authorized request, and traceability of memory updates. The requirements are
implementation-agnostic — they name no storage engine, database, vector store,
or retention algorithm — and complement, rather than replace, existing
governance frameworks (GDPR, EU AI Act, and NIST AI RMF).

Sources:
- https://gdpr-info.eu/art-5-gdpr/
- https://gdpr-info.eu/art-17-gdpr/
- https://gdpr-info.eu/art-32-gdpr/
- https://artificialintelligenceact.eu/
- https://www.nist.gov/itl/ai-risk-management-framework

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-13
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

_GDPR_ART5 = "https://gdpr-info.eu/art-5-gdpr/"
_GDPR_ART17 = "https://gdpr-info.eu/art-17-gdpr/"
_GDPR_ART32 = "https://gdpr-info.eu/art-32-gdpr/"
_EU_AI_ACT = "https://artificialintelligenceact.eu/"
_NIST_AI_RMF = "https://www.nist.gov/itl/ai-risk-management-framework"


def memory_governance() -> list[Requirement]:
    """Governance requirements for how an agent bounds and controls persisted memory."""
    return [
        Requirement(
            id="CAT-AGT-MEM-001",
            statement=(
                "The agent shall isolate persisted memory by user so that memory stored "
                "for one user is not retrievable in another user's session."
            ),
            rationale=(
                "Persisted agent memory often holds personal or sensitive content. "
                "Isolating memory by user or tenant prevents one user's stored content "
                "from leaking into another user's session."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Memory stored for one user is not retrievable in another user's session.",
            ],
            source=[_GDPR_ART32, _EU_AI_ACT, _NIST_AI_RMF],
            priority="blocking",
            standards={
                "gdpr": ["art32"],
                "eu_ai_act": ["euaia-art10"],
                "nist_ai_rmf": ["nist-manage"],
            },
        ),
        Requirement(
            id="CAT-AGT-MEM-002",
            statement=(
                "The agent shall persist and retrieve memory only under an authorization "
                "that permits the operation."
            ),
            rationale=(
                "Unauthorized persistence can capture data that should not be retained, "
                "and unauthorized retrieval can expose stored data. Gating both "
                "operations on authorization keeps memory from being written or read "
                "outside sanctioned use."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "Memory is not persisted unless the operation is authorized.",
                "Memory is not retrieved unless the operation is authorized.",
            ],
            source=[_GDPR_ART32, _EU_AI_ACT, _NIST_AI_RMF],
            priority="blocking",
            standards={
                "gdpr": ["art32"],
                "eu_ai_act": ["euaia-art10"],
                "nist_ai_rmf": ["nist-manage"],
            },
        ),
        Requirement(
            id="CAT-AGT-MEM-003",
            statement=(
                "The agent shall persist only memory content that falls within its "
                "defined memory scope."
            ),
            rationale=(
                "A defined memory scope bounds what the agent is permitted to retain, "
                "preventing the accumulation of content beyond the agent's sanctioned "
                "purpose."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Content that falls outside the agent's defined memory scope is not persisted.",
            ],
            source=[_GDPR_ART5, _EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "gdpr": ["art5-1b"],
                "eu_ai_act": ["euaia-art10"],
                "nist_ai_rmf": ["nist-map"],
            },
        ),
        Requirement(
            id="CAT-AGT-MEM-004",
            statement=("Persisted agent memory shall be removed after a defined retention period."),
            rationale=(
                "Retaining memory without bound increases exposure and conflicts with "
                "storage-limitation principles. Removing memory after a defined "
                "retention period bounds how long content persists."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Persisted agent memory whose age exceeds the defined retention period is removed.",
            ],
            source=[_GDPR_ART5, _EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "gdpr": ["art5-1e"],
                "eu_ai_act": ["euaia-art10"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-MEM-005",
            statement=(
                "The agent shall delete a data subject's persisted memory upon an "
                "authorized deletion request."
            ),
            rationale=(
                "Data subjects have recognized rights to erasure. Deleting a data "
                "subject's persisted memory on an authorized request supports those "
                "rights and any governance-defined deletion policy."
            ),
            verification_method="demonstration",
            acceptance_criteria=[
                "Upon an authorized deletion request for a data subject, that data "
                "subject's persisted memory is deleted.",
            ],
            source=[_GDPR_ART17, _EU_AI_ACT, _NIST_AI_RMF],
            priority="high",
            standards={
                "gdpr": ["art17"],
                "eu_ai_act": ["euaia-art10"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
        Requirement(
            id="CAT-AGT-MEM-006",
            statement=(
                "The system shall record each update to persisted agent memory together "
                "with its initiating context."
            ),
            rationale=(
                "A durable record of memory updates makes changes to what the agent has "
                "retained auditable and supports incident review and data-subject "
                "requests."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Each update to persisted agent memory produces a record containing the "
                "update and its initiating context.",
            ],
            source=[_EU_AI_ACT, _GDPR_ART5, _NIST_AI_RMF],
            priority="high",
            standards={
                "eu_ai_act": ["euaia-art12"],
                "gdpr": ["art5-2"],
                "nist_ai_rmf": ["nist-govern"],
            },
        ),
    ]
