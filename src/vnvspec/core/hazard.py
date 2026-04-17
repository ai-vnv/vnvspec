"""Hazard and HARA (Hazard Analysis and Risk Assessment) models.

A :class:`Hazard` represents an identified hazard with severity, exposure,
and controllability ratings used to determine the Automotive Safety
Integrity Level (ASIL) or equivalent integrity level.

Example:
    >>> h = Hazard(
    ...     id="HAZ-001",
    ...     description="Incorrect object detection leading to late braking.",
    ...     severity="S3",
    ...     exposure="E4",
    ...     controllability="C3",
    ...     asil="D",
    ...     mitigations=["REQ-001", "REQ-002"],
    ... )
    >>> h.asil
    'D'
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

Severity = Literal["S0", "S1", "S2", "S3"]
Exposure = Literal["E0", "E1", "E2", "E3", "E4"]
Controllability = Literal["C0", "C1", "C2", "C3"]
ASIL = Literal["QM", "A", "B", "C", "D"]


class Hazard(BaseModel):
    """A hazard identified through HARA.

    Example:
        >>> h = Hazard(
        ...     id="HAZ-002",
        ...     description="Sensor failure in rain.",
        ...     severity="S2",
        ...     exposure="E3",
        ...     controllability="C2",
        ...     asil="B",
        ... )
        >>> h.id
        'HAZ-002'
    """

    model_config = {"frozen": True}

    id: str = Field(description="Unique hazard identifier, e.g. HAZ-001.")
    description: str = Field(description="Description of the hazard.")
    severity: Severity = Field(description="Severity rating (S0-S3).")
    exposure: Exposure = Field(description="Exposure rating (E0-E4).")
    controllability: Controllability = Field(description="Controllability rating (C0-C3).")
    asil: ASIL = Field(description="Automotive Safety Integrity Level.")
    mitigations: list[str] = Field(
        default_factory=list,
        description="List of requirement IDs that mitigate this hazard.",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary additional metadata."
    )
