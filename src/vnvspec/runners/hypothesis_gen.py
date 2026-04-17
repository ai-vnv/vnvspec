"""Generate hypothesis property tests from an IOContract."""

from __future__ import annotations

import re
import textwrap

from vnvspec.core.contract import IOContract


def _parse_numeric_range(check_expr: str) -> tuple[str, str] | None:
    """Extract (low, high) from expressions like ``0 <= value <= 1``.

    Returns ``None`` when the expression does not match the expected pattern.
    """
    pattern = r"^([+\-]?\d+(?:\.\d+)?)\s*<=\s*value\s*<=\s*([+\-]?\d+(?:\.\d+)?)$"
    match = re.match(pattern, check_expr.strip())
    if match:
        return match.group(1), match.group(2)
    return None


def _strategy_for_invariant(check_expr: str) -> str:
    """Derive a hypothesis strategy string from a *check_expr*."""
    bounds = _parse_numeric_range(check_expr)
    if bounds is not None:
        low, high = bounds
        return f"strategies.floats(min_value={low}, max_value={high})"
    return "strategies.from_type(float)"


def generate_hypothesis(contract: IOContract) -> str:
    """Generate hypothesis property-test source from *contract*.

    For each :class:`~vnvspec.core.contract.Invariant` whose ``check_expr``
    describes a numeric range (e.g. ``"0 <= value <= 1"``), the generated code
    uses ``hypothesis.strategies.floats`` with the extracted bounds.

    Parameters
    ----------
    contract:
        The IO contract to generate tests from.

    Returns
    -------
    str
        Valid Python source code suitable for writing to a ``.py`` file.
    """
    contract_name = contract.name
    lines: list[str] = [
        f'"""Auto-generated hypothesis tests for contract: {contract_name}."""',
        "",
        "from __future__ import annotations",
        "",
        "from hypothesis import given, strategies",
        "",
    ]

    if not contract.invariants:
        lines.append("")
        return "\n".join(lines)

    for inv in contract.invariants:
        strategy = _strategy_for_invariant(inv.check_expr)
        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", inv.name).strip("_").lower()
        func_name = f"test_{safe_name}"

        block = textwrap.dedent(f"""\
            @given(value={strategy})
            def {func_name}(value: float) -> None:
                \"\"\"{inv.description or inv.name}\"\"\"
                assert {inv.check_expr or "True"}
        """)
        lines.append(block)
        lines.append("")

    return "\n".join(lines)
