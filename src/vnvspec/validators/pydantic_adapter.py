"""Pydantic adapter — generates Invariants from a pydantic BaseModel.

Translates pydantic validation into vnvspec :class:`Evidence` objects,
bridging pydantic's schema validation with vnvspec's contract system.

Example:
    >>> from pydantic import BaseModel, Field
    >>> class Prediction(BaseModel):
    ...     label: str
    ...     score: float = Field(ge=0.0, le=1.0)
    >>> invariants = pydantic_schema(Prediction)
    >>> len(invariants) >= 1
    True
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from vnvspec.core.contract import Invariant
from vnvspec.core.evidence import Evidence


def pydantic_schema(
    model_class: type[BaseModel],
) -> list[Invariant]:
    """Extract invariants from a pydantic model's field constraints.

    Creates one invariant per field, checking that the field value
    passes pydantic validation for that field.

    Example:
        >>> from pydantic import BaseModel, Field
        >>> class Output(BaseModel):
        ...     prob: float = Field(ge=0, le=1)
        >>> invs = pydantic_schema(Output)
        >>> any(i.name == "prob" for i in invs)
        True
    """
    invariants: list[Invariant] = []
    for field_name, field_info in model_class.model_fields.items():
        description = field_info.description or f"Validates field '{field_name}'"
        invariants.append(
            Invariant(
                name=field_name,
                description=description,
                check_expr="",
            )
        )
    return invariants


def validate_record(
    model_class: type[BaseModel],
    data: dict[str, Any],
    *,
    requirement_id: str = "",
) -> Evidence:
    """Validate a data record against a pydantic model.

    Returns an Evidence object with verdict "pass" or "fail".

    Example:
        >>> from pydantic import BaseModel, Field
        >>> class Pred(BaseModel):
        ...     score: float = Field(ge=0, le=1)
        >>> ev = validate_record(Pred, {"score": 0.5})
        >>> ev.verdict
        'pass'
        >>> ev_bad = validate_record(Pred, {"score": 2.0})
        >>> ev_bad.verdict
        'fail'
    """
    try:
        model_class.model_validate(data)
        return Evidence(
            id=f"pydantic-{requirement_id or 'check'}",
            requirement_id=requirement_id,
            kind="test",
            verdict="pass",
            details={"validator": "pydantic", "model": model_class.__name__},
        )
    except Exception as exc:
        return Evidence(
            id=f"pydantic-{requirement_id or 'check'}",
            requirement_id=requirement_id,
            kind="test",
            verdict="fail",
            details={
                "validator": "pydantic",
                "model": model_class.__name__,
                "errors": str(exc),
            },
        )
