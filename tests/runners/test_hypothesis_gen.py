"""Tests for vnvspec.runners.hypothesis_gen."""

from __future__ import annotations

from vnvspec.core.contract import Invariant, IOContract
from vnvspec.runners.hypothesis_gen import generate_hypothesis


def test_generate_hypothesis_numeric_range() -> None:
    """A numeric range invariant produces a floats strategy with bounds."""
    inv = Invariant(
        name="probability_range",
        description="Output probability in [0, 1]",
        check_expr="0 <= value <= 1",
    )
    contract = IOContract(name="classifier-io", invariants=[inv])
    code = generate_hypothesis(contract)

    assert "strategies.floats(min_value=0, max_value=1)" in code
    assert "def test_probability_range(" in code


def test_generate_hypothesis_docstring() -> None:
    """Invariant description appears in the test docstring."""
    inv = Invariant(
        name="score_bound",
        description="Score must be between 0 and 100",
        check_expr="0 <= value <= 100",
    )
    contract = IOContract(name="scorer", invariants=[inv])
    code = generate_hypothesis(contract)

    assert "Score must be between 0 and 100" in code


def test_generate_hypothesis_fallback_strategy() -> None:
    """Non-numeric invariants fall back to from_type(float)."""
    inv = Invariant(
        name="custom_check",
        description="Custom invariant",
        check_expr="value > 0",
    )
    contract = IOContract(name="custom", invariants=[inv])
    code = generate_hypothesis(contract)

    assert "strategies.from_type(float)" in code


def test_generate_hypothesis_empty_contract() -> None:
    """A contract with no invariants produces valid but empty test code."""
    contract = IOContract(name="empty")
    code = generate_hypothesis(contract)

    assert "def test_" not in code
    assert "empty" in code


def test_generate_hypothesis_output_is_valid_python() -> None:
    """The generated string compiles as valid Python."""
    inv = Invariant(
        name="valid_range",
        description="Value in [0, 1]",
        check_expr="0 <= value <= 1",
    )
    contract = IOContract(name="compile-test", invariants=[inv])
    code = generate_hypothesis(contract)

    compile(code, "<generated>", "exec")


def test_generate_hypothesis_multiple_invariants() -> None:
    """Multiple invariants each get their own test function."""
    inv1 = Invariant(name="low_bound", check_expr="0 <= value <= 1")
    inv2 = Invariant(name="high_bound", check_expr="-10 <= value <= 10")
    contract = IOContract(name="multi", invariants=[inv1, inv2])
    code = generate_hypothesis(contract)

    assert "def test_low_bound(" in code
    assert "def test_high_bound(" in code
    assert "strategies.floats(min_value=0, max_value=1)" in code
    assert "strategies.floats(min_value=-10, max_value=10)" in code
