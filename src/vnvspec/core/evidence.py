"""Evidence model — records of verification activities.

An :class:`Evidence` object records the outcome of a verification activity
(test, analysis, inspection, demonstration, or simulation) against a
specific requirement.

Example:
    >>> from datetime import datetime, timezone
    >>> e = Evidence(
    ...     id="EV-001",
    ...     requirement_id="REQ-001",
    ...     kind="test",
    ...     verdict="pass",
    ...     observed_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
    ... )
    >>> e.verdict
    'pass'
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

EvidenceKind = Literal[
    "test", "analysis", "inspection", "demonstration", "simulation", "formal_proof"
]
Verdict = Literal["pass", "fail", "inconclusive"]


class Evidence(BaseModel):
    """A single piece of verification evidence.

    The ``details`` field accepts either a ``dict`` or a plain ``str``.
    A bare string is automatically wrapped into ``{"message": "..."}``
    so the on-disk JSON shape stays stable.

    Example:
        >>> e = Evidence(
        ...     id="EV-002",
        ...     requirement_id="REQ-002",
        ...     kind="analysis",
        ...     verdict="pass",
        ...     details="looks good",
        ... )
        >>> e.details
        {'message': 'looks good'}
    """

    model_config = {"frozen": True}

    id: str = Field(description="Unique evidence identifier, e.g. EV-001.")
    requirement_id: str = Field(description="ID of the requirement this evidence is for.")
    kind: EvidenceKind = Field(description="Type of verification activity.")
    verdict: Verdict = Field(description="Outcome: pass, fail, or inconclusive.")
    artifact_uri: str = Field(default="", description="URI or path to the evidence artifact.")
    observed_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="When the evidence was collected.",
    )
    details: dict[str, Any] = Field(
        default_factory=dict, description="Additional details about the evidence."
    )

    @model_validator(mode="before")
    @classmethod
    def _wrap_str_details(cls, data: Any) -> Any:
        """Auto-wrap a bare ``str`` details value into ``{"message": ...}``."""
        if isinstance(data, dict) and "details" in data and isinstance(data["details"], str):
            data = {**data, "details": {"message": data["details"]}}
        return data
