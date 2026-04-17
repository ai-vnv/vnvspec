"""Tests for the IOContract and Invariant models."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from vnvspec.core.contract import Invariant, IOContract


class TestInvariant:
    def test_construction(self) -> None:
        inv = Invariant(name="positive", check_expr="value > 0")
        assert inv.name == "positive"

    def test_check_passes(self) -> None:
        inv = Invariant(name="positive", check_expr="value > 0")
        assert inv.check(5) is True

    def test_check_fails(self) -> None:
        inv = Invariant(name="positive", check_expr="value > 0")
        assert inv.check(-1) is False

    def test_check_empty_expr(self) -> None:
        inv = Invariant(name="always_true")
        assert inv.check(42) is True

    def test_check_invalid_expr(self) -> None:
        inv = Invariant(name="broken", check_expr="value / 0")
        assert inv.check(1) is False

    def test_frozen(self) -> None:
        inv = Invariant(name="test")
        with pytest.raises(ValidationError):
            inv.name = "other"  # type: ignore[misc]

    def test_json_round_trip(self) -> None:
        inv = Invariant(name="range", check_expr="0 <= value <= 1", description="Probability range")
        data = json.loads(inv.model_dump_json())
        inv2 = Invariant.model_validate(data)
        assert inv == inv2


class TestIOContract:
    def test_construction(self) -> None:
        contract = IOContract(
            name="classifier",
            inputs={"image": {"type": "tensor"}},
            outputs={"label": {"type": "str"}},
        )
        assert contract.name == "classifier"

    def test_check_invariants_pass(self) -> None:
        inv = Invariant(name="prob", check_expr="0 <= value <= 1")
        contract = IOContract(name="test", invariants=[inv])
        results = contract.check_invariants({"prob": 0.5})
        assert results == {"prob": True}

    def test_check_invariants_fail(self) -> None:
        inv = Invariant(name="prob", check_expr="0 <= value <= 1")
        contract = IOContract(name="test", invariants=[inv])
        results = contract.check_invariants({"prob": 1.5})
        assert results == {"prob": False}

    def test_check_invariants_missing_value(self) -> None:
        inv = Invariant(name="prob", check_expr="value is not None")
        contract = IOContract(name="test", invariants=[inv])
        results = contract.check_invariants({})
        assert results == {"prob": False}

    def test_multiple_invariants(self) -> None:
        inv1 = Invariant(name="pos", check_expr="value > 0")
        inv2 = Invariant(name="small", check_expr="value < 100")
        contract = IOContract(name="test", invariants=[inv1, inv2])
        results = contract.check_invariants({"pos": 5, "small": 50})
        assert results == {"pos": True, "small": True}

    def test_json_round_trip(self) -> None:
        inv = Invariant(name="test", check_expr="value > 0")
        contract = IOContract(name="c", inputs={"x": 1}, outputs={"y": 2}, invariants=[inv])
        data = json.loads(contract.model_dump_json())
        contract2 = IOContract.model_validate(data)
        assert contract.name == contract2.name
        assert len(contract2.invariants) == 1
