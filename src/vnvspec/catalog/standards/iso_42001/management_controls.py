"""ISO/IEC 42001 Management System Controls — Clauses 4 through 10.

This module provides reusable requirements for organizational AI management
system (AIMS) controls specified in Clauses 4 to 10 of ISO/IEC 42001:2023.

It is a baseline, not a substitute for expert review.

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-26
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

_ISO_42001_URL = "https://www.iso.org/standard/81230.html"


def management_controls() -> list[Requirement]:
    """Return reusable requirements for ISO/IEC 42001 Clauses 4 through 10."""
    return [
        Requirement(
            id="CAT-ISO-MGT-001",
            statement=(
                "The organization shall document the external and internal context issues "
                "relevant to its AI management system."
            ),
            rationale=(
                "Clause 4.1 requires identifying external and internal factors that affect "
                "the organization's ability to achieve the intended outcomes of its AIMS."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A documented context assessment exists listing internal and external AI risks.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["4.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-002",
            statement=(
                "The organization shall establish and maintain a documented AI policy "
                "approved by top management."
            ),
            rationale=(
                "Clause 5.2 mandates an organizational policy providing direction for "
                "governing AI system development and deployment."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "An AI policy document approved by top management is accessible to stakeholders.",
            ],
            source=[_ISO_42001_URL],
            priority="blocking",
            standards={
                "iso_42001": ["5.2"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-003",
            statement=(
                "The organization shall assign and document specific roles and responsibilities "
                "for governing AI risk."
            ),
            rationale=(
                "Clause 5.3 requires clear lines of authority and accountability across "
                "the AI system lifecycle."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A RACI matrix or role assignment document for AI risk management is maintained.",
            ],
            source=[_ISO_42001_URL],
            priority="blocking",
            standards={
                "iso_42001": ["5.3"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-004",
            statement=(
                "The organization shall record identified AI risks and planned risk "
                "treatment actions."
            ),
            rationale=(
                "Clause 6.1 requires systematic identification and planning to address "
                "AI-specific technical and ethical risks."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "An AI risk register detailing risk identification and treatment plans "
                "is maintained.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["6.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-005",
            statement=("The organization shall maintain documented measurable AI objectives."),
            rationale=(
                "Clause 6.2 mandates setting measurable objectives consistent with the AI policy."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Documented AI objectives with defined metrics and evaluation criteria exist.",
            ],
            source=[_ISO_42001_URL],
            priority="medium",
            standards={
                "iso_42001": ["6.2"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-006",
            statement=(
                "The organization shall verify the technical competence of personnel who manage "
                "or operate AI systems."
            ),
            rationale=(
                "Clause 7.2 requires determining competence requirements and ensuring personnel "
                "possess necessary education, training, or experience."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Training and qualification records exist for all AI system operators.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["7.2"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-007",
            statement=(
                "The organization shall establish documented controls for AI system "
                "operational planning."
            ),
            rationale=(
                "Clause 8.1 mandates operational planning and control to implement risk treatments."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Documented standard operating procedures for AI system operations are published.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["8.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-008",
            statement=(
                "The organization shall perform a documented AI system impact assessment "
                "prior to deployment."
            ),
            rationale=(
                "Clause 8.3 requires assessing potential impacts on individuals, groups, and "
                "society before deploying an AI system."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A signed AI system impact assessment (AISIA) report exists for the system.",
            ],
            source=[_ISO_42001_URL],
            priority="blocking",
            standards={
                "iso_42001": ["8.3"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-009",
            statement=(
                "The organization shall record performance metrics for the AI management "
                "system at planned intervals."
            ),
            rationale=("Clause 9.1 requires monitoring and evaluating AIMS performance."),
            verification_method="inspection",
            acceptance_criteria=[
                "Performance evaluation records containing monitoring results are "
                "produced periodically.",
            ],
            source=[_ISO_42001_URL],
            priority="medium",
            standards={
                "iso_42001": ["9.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-010",
            statement=(
                "The organization shall conduct internal audits of the AI management system "
                "at planned intervals."
            ),
            rationale=("Clause 9.2 mandates periodic internal audits to ensure AIMS conformance."),
            verification_method="inspection",
            acceptance_criteria=[
                "An internal audit report evaluating AIMS compliance is published annually.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["9.2"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-011",
            statement=(
                "Top management shall conduct documented management reviews of the AI "
                "management system."
            ),
            rationale=(
                "Clause 9.3 mandates management review of the AIMS to ensure continuing "
                "suitability."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Management review meeting minutes and action item logs exist.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["9.3"],
            },
        ),
        Requirement(
            id="CAT-ISO-MGT-012",
            statement=(
                "The organization shall document corrective actions for identified "
                "nonconformities in the AI management system."
            ),
            rationale=(
                "Clause 10.1 requires taking action to eliminate root causes of nonconformities."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Corrective action logs tracking nonconformity resolutions are maintained.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["10.1"],
            },
        ),
    ]
