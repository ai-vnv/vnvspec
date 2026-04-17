"""Assessment context and report models.

An :class:`AssessmentContext` carries state during an assessment run.
A :class:`Report` aggregates evidence from an assessment.

Example:
    >>> report = Report(spec_name="test", spec_version="0.1.0")
    >>> report.spec_name
    'test'
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from vnvspec.core.evidence import Evidence


class AssessmentContext(BaseModel):
    """Mutable context passed through an assessment run.

    Example:
        >>> ctx = AssessmentContext(run_id="run-001")
        >>> ctx.run_id
        'run-001'
    """

    run_id: str = Field(default="", description="Unique run identifier.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Runtime metadata.")


class Report(BaseModel):
    """Assessment report aggregating evidence.

    The ``summary`` field accepts either a ``dict`` or a plain ``str``.
    A bare string is automatically wrapped into ``{"message": "..."}``
    so the on-disk JSON shape stays stable.

    Example:
        >>> r = Report(spec_name="my-spec", spec_version="1.0")
        >>> len(r.evidence)
        0
    """

    spec_name: str = Field(description="Name of the assessed spec.")
    spec_version: str = Field(default="", description="Spec version.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Report creation timestamp.",
    )
    evidence: list[Evidence] = Field(default_factory=list, description="Collected evidence.")
    summary: dict[str, Any] = Field(default_factory=dict, description="Summary statistics.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata.")

    @model_validator(mode="before")
    @classmethod
    def _wrap_str_summary(cls, data: Any) -> Any:
        """Auto-wrap a bare ``str`` summary value into ``{"message": ...}``."""
        if isinstance(data, dict) and "summary" in data and isinstance(data["summary"], str):
            data = {**data, "summary": {"message": data["summary"]}}
        return data

    def pass_count(self) -> int:
        """Count evidence with pass verdict.

        Example:
            >>> r = Report(spec_name="test")
            >>> r.pass_count()
            0
        """
        return sum(1 for e in self.evidence if e.verdict == "pass")

    def fail_count(self) -> int:
        """Count evidence with fail verdict.

        Example:
            >>> r = Report(spec_name="test")
            >>> r.fail_count()
            0
        """
        return sum(1 for e in self.evidence if e.verdict == "fail")

    def verdict(self) -> str:
        """Overall verdict: 'pass' if no fails, 'fail' otherwise.

        Returns 'inconclusive' if no evidence exists.

        Example:
            >>> r = Report(spec_name="test")
            >>> r.verdict()
            'inconclusive'
        """
        if not self.evidence:
            return "inconclusive"
        return "fail" if self.fail_count() > 0 else "pass"
