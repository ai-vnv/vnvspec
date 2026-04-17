"""Tests for vnvspec.runners.pytest_gen."""

from __future__ import annotations

from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.runners.pytest_gen import generate_pytest


def test_generate_pytest_contains_test_functions() -> None:
    """A spec with test requirements produces named test functions."""
    req = Requirement(
        id="REQ-001",
        statement="The model shall output valid probabilities.",
        verification_method="test",
        acceptance_criteria=["probability in [0, 1]"],
    )
    spec = Spec(name="toy-spec", requirements=[req])
    code = generate_pytest(spec)

    assert "def test_req_001(" in code
    assert "REQ-001" in code


def test_generate_pytest_includes_docstrings() -> None:
    """Each generated test function has a docstring with requirement ID and statement."""
    req = Requirement(
        id="REQ-002",
        statement="Latency under 100ms.",
        verification_method="test",
        acceptance_criteria=["p99 < 100ms"],
    )
    spec = Spec(name="latency-spec", requirements=[req])
    code = generate_pytest(spec)

    assert "REQ-002: Latency under 100ms." in code


def test_generate_pytest_skips_non_test_methods() -> None:
    """Requirements with verification_method != 'test' are excluded."""
    req_test = Requirement(
        id="REQ-T1",
        statement="Testable requirement.",
        verification_method="test",
    )
    req_analysis = Requirement(
        id="REQ-A1",
        statement="Analysis requirement.",
        verification_method="analysis",
    )
    spec = Spec(name="mixed-spec", requirements=[req_test, req_analysis])
    code = generate_pytest(spec)

    assert "test_req_t1" in code
    assert "req_a1" not in code


def test_generate_pytest_parametrize() -> None:
    """Acceptance criteria become pytest.mark.parametrize values."""
    req = Requirement(
        id="REQ-003",
        statement="Multiple criteria.",
        verification_method="test",
        acceptance_criteria=["crit_a", "crit_b"],
    )
    spec = Spec(name="param-spec", requirements=[req])
    code = generate_pytest(spec)

    assert "@pytest.mark.parametrize" in code
    assert "'crit_a'" in code
    assert "'crit_b'" in code


def test_generate_pytest_empty_spec() -> None:
    """An empty spec produces valid but empty test code."""
    spec = Spec(name="empty-spec")
    code = generate_pytest(spec)

    assert "def test_" not in code
    assert "empty-spec" in code


def test_generate_pytest_output_is_valid_python() -> None:
    """The generated string compiles as valid Python."""
    req = Requirement(
        id="REQ-005",
        statement="Valid Python output.",
        verification_method="test",
        acceptance_criteria=["check"],
    )
    spec = Spec(name="compile-spec", requirements=[req])
    code = generate_pytest(spec)

    compile(code, "<generated>", "exec")
