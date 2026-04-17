"""Requirement model — the atomic unit of a V&V specification.

A Requirement captures a single, verifiable statement about a system's
expected behavior, along with metadata for traceability and quality checking.

Example:
    >>> req = Requirement(
    ...     id="REQ-001",
    ...     statement="The system shall classify images with accuracy above 0.9.",
    ...     rationale="High accuracy is needed for safety-critical deployment.",
    ...     verification_method="test",
    ...     acceptance_criteria=["Accuracy > 0.9 on the test set."],
    ... )
    >>> req.id
    'REQ-001'
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, Field, model_validator

if TYPE_CHECKING:
    from vnvspec.core._internal.gtwr_rules import RuleProfile, RuleViolation

VerificationMethod = Literal[
    "test", "analysis", "inspection", "demonstration", "simulation", "formal_proof"
]
Priority = Literal["blocking", "high", "medium", "low"]


class Requirement(BaseModel):
    """A single V&V requirement.

    The ``source`` field accepts a single string (auto-normalized to a
    one-element list) or a list of strings. An empty string is normalized
    to an empty list for consistency.

    Example:
        >>> r = Requirement(
        ...     id="REQ-002",
        ...     statement="The system shall respond within 100 ms.",
        ...     rationale="Latency budget from system architecture.",
        ...     verification_method="test",
        ...     acceptance_criteria=["p99 latency < 100 ms"],
        ... )
        >>> r.verification_method
        'test'
    """

    model_config = {"frozen": True}

    id: str = Field(description="Unique requirement identifier, e.g. REQ-001.")
    statement: str = Field(description="The requirement statement (shall-language).")
    rationale: str = Field(default="", description="Why this requirement exists.")
    source: list[str] = Field(
        default_factory=list,
        description="Source URLs or references for this requirement.",
    )
    priority: Priority = Field(default="medium", description="Requirement priority level.")

    @model_validator(mode="before")
    @classmethod
    def _normalize_source(cls, data: Any) -> Any:
        """Normalize source: str → list[str], empty str → []."""
        if isinstance(data, dict) and "source" in data:
            src = data["source"]
            if isinstance(src, str):
                data = {**data, "source": [src] if src else []}
        return data

    verification_method: VerificationMethod = Field(
        default="test", description="How the requirement is verified."
    )
    standards: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Mapping of standard name to clause ids, e.g. {'iso_pas_8800': ['6.2.1']}.",
    )
    ontology_refs: list[str] = Field(
        default_factory=list, description="References to ontology concepts."
    )
    acceptance_criteria: list[str] = Field(
        default_factory=list, description="Concrete criteria for pass/fail determination."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary additional metadata."
    )

    def check_quality(self, profile: RuleProfile | None = None) -> list[RuleViolation]:
        """Run INCOSE GtWR rule checks against this requirement.

        Parameters
        ----------
        profile:
            Optional rule profile (``"formal"``, ``"web-app"``, ``"embedded"``).
            Defaults to ``"formal"`` if not specified.

        Returns a list of :class:`RuleViolation` objects, one per failing rule.
        An empty list means the requirement passes all quality checks.

        Example:
            >>> r = Requirement(id="REQ-BAD", statement="The system should work.")
            >>> violations = r.check_quality()
            >>> len(violations) > 0
            True
        """
        from vnvspec.core._internal.gtwr_rules import (  # noqa: PLC0415
            RuleProfile,
            check_all,
        )

        if profile is None:
            profile = RuleProfile.FORMAL
        return check_all(self, profile=profile)
