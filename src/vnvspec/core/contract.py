"""Input-output contract model for system interfaces.

An :class:`IOContract` defines the expected input schema, output schema,
and invariants that must hold for a system's interface.

Example:
    >>> inv = Invariant(
    ...     name="probability_range",
    ...     description="Output probability in [0, 1]",
    ...     check_expr="0 <= value <= 1",
    ... )
    >>> contract = IOContract(
    ...     name="classifier-io",
    ...     inputs={"image": {"type": "tensor", "shape": [3, 224, 224]}},
    ...     outputs={"probability": {"type": "float", "range": [0.0, 1.0]}},
    ...     invariants=[inv],
    ... )
    >>> contract.name
    'classifier-io'
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Invariant(BaseModel):
    """A single invariant that must hold for a contract.

    Example:
        >>> inv = Invariant(
        ...     name="non_negative",
        ...     description="Value must be non-negative",
        ...     check_expr="value >= 0",
        ... )
        >>> inv.name
        'non_negative'
    """

    model_config = {"frozen": True}

    name: str = Field(description="Short invariant name.")
    description: str = Field(default="", description="Human-readable description.")
    check_expr: str = Field(
        default="",
        description="A Python expression string (with 'value' as the variable) to check.",
    )

    def check(self, value: Any) -> bool:
        """Evaluate the invariant against a value.

        Returns True if the invariant holds, False otherwise.
        If ``check_expr`` is empty, always returns True.

        Example:
            >>> inv = Invariant(name="positive", check_expr="value > 0")
            >>> inv.check(5)
            True
            >>> inv.check(-1)
            False
        """
        if not self.check_expr:
            return True
        try:
            return bool(eval(self.check_expr, {"__builtins__": {}}, {"value": value}))
        except Exception:
            return False


class IOContract(BaseModel):
    """Input-output contract for a system interface.

    Example:
        >>> contract = IOContract(
        ...     name="simple",
        ...     inputs={"x": {"type": "float"}},
        ...     outputs={"y": {"type": "float"}},
        ... )
        >>> contract.name
        'simple'
    """

    model_config = {"frozen": True}

    name: str = Field(description="Contract name.")
    description: str = Field(default="", description="Human-readable description.")
    inputs: dict[str, Any] = Field(default_factory=dict, description="Input schema as a dict.")
    outputs: dict[str, Any] = Field(default_factory=dict, description="Output schema as a dict.")
    invariants: list[Invariant] = Field(
        default_factory=list, description="Invariants that must hold."
    )

    def check_invariants(self, values: dict[str, Any]) -> dict[str, bool]:
        """Check all invariants against a dict of named values.

        Returns a mapping from invariant name to pass/fail.

        Example:
            >>> inv = Invariant(name="pos", check_expr="value > 0")
            >>> c = IOContract(name="test", invariants=[inv])
            >>> c.check_invariants({"pos": 5})
            {'pos': True}
        """
        results: dict[str, bool] = {}
        for invariant in self.invariants:
            val = values.get(invariant.name)
            results[invariant.name] = invariant.check(val)
        return results
