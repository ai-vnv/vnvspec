"""Pandera adapter — validates DataFrames against pandera schemas.

Translates pandera schema validation into vnvspec :class:`Evidence` objects.

Example:
    >>> import pandera as pa
    >>> schema = pa.DataFrameSchema({"score": pa.Column(float, pa.Check.in_range(0, 1))})
    >>> invariants = pandera_schema(schema)
    >>> len(invariants) >= 1
    True
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from vnvspec.core.contract import Invariant
from vnvspec.core.evidence import Evidence

if TYPE_CHECKING:
    import pandas as pd
    import pandera as pa


def pandera_schema(
    schema: pa.DataFrameSchema,
) -> list[Invariant]:
    """Extract invariants from a pandera DataFrameSchema.

    Creates one invariant per column in the schema.

    Example:
        >>> import pandera as pa
        >>> schema = pa.DataFrameSchema({
        ...     "x": pa.Column(int),
        ...     "y": pa.Column(float),
        ... })
        >>> invs = pandera_schema(schema)
        >>> len(invs)
        2
    """
    invariants: list[Invariant] = []
    columns: dict[str, Any] = schema.columns
    for col_name in columns:
        invariants.append(
            Invariant(
                name=str(col_name),
                description=f"Pandera check for column '{col_name}'",
                check_expr="",
            )
        )
    return invariants


def validate_dataframe(
    schema: pa.DataFrameSchema,
    df: pd.DataFrame,
    *,
    requirement_id: str = "",
) -> Evidence:
    """Validate a DataFrame against a pandera schema.

    Returns an Evidence object with verdict "pass" or "fail".

    Example:
        >>> import pandas as pd
        >>> import pandera as pa
        >>> schema = pa.DataFrameSchema({"x": pa.Column(int, pa.Check.gt(0))})
        >>> df_good = pd.DataFrame({"x": [1, 2, 3]})
        >>> ev = validate_dataframe(schema, df_good)
        >>> ev.verdict
        'pass'
    """
    try:
        schema.validate(df)
        return Evidence(
            id=f"pandera-{requirement_id or 'check'}",
            requirement_id=requirement_id,
            kind="test",
            verdict="pass",
            details={"validator": "pandera", "rows": len(df)},
        )
    except Exception as exc:
        return Evidence(
            id=f"pandera-{requirement_id or 'check'}",
            requirement_id=requirement_id,
            kind="test",
            verdict="fail",
            details={
                "validator": "pandera",
                "rows": len(df),
                "errors": str(exc),
            },
        )
