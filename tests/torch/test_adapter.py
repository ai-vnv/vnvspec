"""Tests for TorchAdapter (requires torch)."""

from __future__ import annotations

from typing import Any

import pytest

torch = pytest.importorskip("torch")

from vnvspec.core.protocols import ModelAdapter
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.torch.adapter import TorchAdapter
from vnvspec.torch.hooks import HookManager, TensorSummary


class SimpleMLP(torch.nn.Module):
    """A 3-layer MLP for testing."""

    def __init__(self, in_features: int = 10, out_features: int = 2) -> None:
        super().__init__()
        self.fc1 = torch.nn.Linear(in_features, 32)
        self.relu = torch.nn.ReLU()
        self.fc2 = torch.nn.Linear(32, out_features)
        self.softmax = torch.nn.Softmax(dim=-1)

    def forward(self, x: Any) -> Any:
        x = self.relu(self.fc1(x))
        return self.softmax(self.fc2(x))


@pytest.fixture()
def mlp() -> torch.nn.Module:
    return SimpleMLP()


@pytest.fixture()
def adapter(mlp: torch.nn.Module) -> TorchAdapter:
    return TorchAdapter(mlp, device="cpu", sample_budget=20, batch_size=8)


@pytest.fixture()
def sample_spec() -> Spec:
    return Spec(
        name="test-mlp",
        requirements=[
            Requirement(
                id="REQ-001",
                statement="The model shall produce probabilities in [0, 1].",
                rationale="Valid probability outputs.",
                verification_method="test",
                acceptance_criteria=["All outputs in [0, 1]."],
            ),
            Requirement(
                id="REQ-002",
                statement="The model shall produce 2 output classes.",
                rationale="Binary classification.",
                verification_method="test",
                acceptance_criteria=["Output dim == 2."],
            ),
        ],
    )


class TestTorchAdapter:
    def test_satisfies_model_adapter(self, adapter: TorchAdapter) -> None:
        assert isinstance(adapter, ModelAdapter)

    def test_forward(self, adapter: TorchAdapter) -> None:
        x = torch.randn(4, 10)
        output = adapter.forward(x)
        assert output.shape == (4, 2)

    def test_output_probabilities(self, adapter: TorchAdapter) -> None:
        x = torch.randn(4, 10)
        output = adapter.forward(x)
        assert (output >= 0).all()
        assert (output <= 1).all()

    def test_describe(self, adapter: TorchAdapter) -> None:
        desc = adapter.describe()
        assert desc["class"] == "SimpleMLP"
        assert desc["device"] == "cpu"
        assert desc["parameters"] > 0

    def test_batch_size_hint(self, adapter: TorchAdapter) -> None:
        assert adapter.batch_size_hint() == 8

    def test_supports_streaming(self, adapter: TorchAdapter) -> None:
        assert adapter.supports_streaming() is False

    def test_non_module_raises(self) -> None:
        with pytest.raises(TypeError, match=r"nn\.Module"):
            TorchAdapter("not a model")

    def test_assess_produces_report(
        self,
        adapter: TorchAdapter,
        sample_spec: Spec,
    ) -> None:
        data = [torch.randn(10) for _ in range(20)]
        report = adapter.assess(sample_spec, data)
        assert report.spec_name == "test-mlp"
        assert len(report.evidence) == 2
        for ev in report.evidence:
            assert ev.verdict in ("pass", "fail", "inconclusive")

    def test_assess_empty_data(
        self,
        adapter: TorchAdapter,
        sample_spec: Spec,
    ) -> None:
        report = adapter.assess(sample_spec, [])
        assert len(report.evidence) == 2
        for ev in report.evidence:
            assert ev.verdict == "inconclusive"


class TestHookManager:
    def test_attach_and_observe(self, mlp: torch.nn.Module) -> None:
        hm = HookManager()
        hm.attach(mlp)
        x = torch.randn(2, 10)
        mlp(x)
        assert len(hm.observations) > 0
        hm.detach()

    def test_summary_recorded(self, mlp: torch.nn.Module) -> None:
        hm = HookManager()
        hm.attach(mlp)
        x = torch.randn(2, 10)
        mlp(x)
        for summaries in hm.observations.values():
            for s in summaries:
                assert isinstance(s, TensorSummary)
                assert len(s.shape) > 0
        hm.detach()

    def test_clear(self, mlp: torch.nn.Module) -> None:
        hm = HookManager()
        hm.attach(mlp)
        x = torch.randn(2, 10)
        mlp(x)
        assert len(hm.observations) > 0
        hm.clear()
        assert len(hm.observations) == 0
        hm.detach()

    def test_non_module_raises(self) -> None:
        hm = HookManager()
        with pytest.raises(TypeError, match=r"nn\.Module"):
            hm.attach("not a model")
