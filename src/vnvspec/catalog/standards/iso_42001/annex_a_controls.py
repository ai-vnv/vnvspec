"""ISO/IEC 42001 Annex A AI Controls.

This module provides reusable requirements for Annex A AI Controls specified in
ISO/IEC 42001:2023.

It is a baseline, not a substitute for expert review.

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-26
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

_ISO_42001_URL = "https://www.iso.org/standard/81230.html"


def annex_a_controls() -> list[Requirement]:
    """Return reusable requirements for ISO/IEC 42001 Annex A AI Controls."""
    return [
        Requirement(
            id="CAT-ISO-ANN-001",
            statement=(
                "The organization shall align AI system operational policies with "
                "enterprise risk policies."
            ),
            rationale=(
                "Control A.2.1 ensures AI policies do not operate in isolation from general "
                "risk management policies."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Documented alignment mapping exists between AI policy and enterprise risk policy.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.2.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-002",
            statement=(
                "The organization shall document technical responsibilities for AI system "
                "developers and deployers."
            ),
            rationale=(
                "Control A.3.1 requires defining technical roles specific to AI engineering."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Written role descriptions exist for AI system development and deployment leads.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.3.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-003",
            statement=(
                "The organization shall allocate qualified human resources for AI system oversight."
            ),
            rationale=(
                "Control A.4.1 ensures adequate human resources are assigned to oversight "
                "functions."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Resource allocation plans show dedicated oversight personnel for AI systems.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.4.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-004",
            statement=(
                "The organization shall conduct an AI system impact assessment prior to "
                "system deployment."
            ),
            rationale=(
                "Control A.5.1 requires evaluating societal and ethical impacts before deployment."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "An impact assessment document covering societal and individual "
                "safety is approved.",
            ],
            source=[_ISO_42001_URL],
            priority="blocking",
            standards={
                "iso_42001": ["A.5.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-005",
            statement=(
                "The organization shall establish documented lifecycle management procedures "
                "for AI systems."
            ),
            rationale=(
                "Control A.6.1 mandates managing AI systems across design, deployment, and "
                "decommissioning."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A lifecycle process specification exists covering all phases of the AI system.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.6.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-006",
            statement=(
                "The organization shall execute verification and validation activities for "
                "each AI system."
            ),
            rationale=(
                "Control A.6.2 requires rigorous testing and evidence collection prior to "
                "operational use."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A test summary report demonstrating requirement satisfaction is signed.",
            ],
            source=[_ISO_42001_URL],
            priority="blocking",
            standards={
                "iso_42001": ["A.6.2"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-007",
            statement=(
                "The organization shall record the provenance of training and testing datasets."
            ),
            rationale=(
                "Control A.7.1 requires establishing data quality, lineage, and licensing "
                "governance."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A dataset lineage sheet documenting source, licensing, and preprocessing exists.",
            ],
            source=[_ISO_42001_URL],
            priority="blocking",
            standards={
                "iso_42001": ["A.7.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-008",
            statement=(
                "The organization shall provide system documentation detailing operational "
                "limits to users."
            ),
            rationale=(
                "Control A.8.1 mandates user transparency regarding system capabilities and "
                "constraints."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "A user manual or system card detailing operational bounds is published.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.8.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-009",
            statement=(
                "The organization shall establish acceptable use guidelines for internal "
                "AI system deployment."
            ),
            rationale=(
                "Control A.9.1 requires defining authorized and prohibited use cases for "
                "internal users."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Acceptable use guidelines are published and communicated to all internal users.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.9.1"],
            },
        ),
        Requirement(
            id="CAT-ISO-ANN-010",
            statement=(
                "The organization shall evaluate third-party AI components against "
                "organizational safety policies."
            ),
            rationale=(
                "Control A.10.1 requires assessing risks from supplier-provided models or datasets."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Supplier evaluation reports exist for all third-party AI models or services.",
            ],
            source=[_ISO_42001_URL],
            priority="high",
            standards={
                "iso_42001": ["A.10.1"],
            },
        ),
    ]
