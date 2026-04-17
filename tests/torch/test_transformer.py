"""Tests for TransformerAdapter.

These tests use prajjwal1/bert-tiny (4.4M params) for speed.
Marked as slow since they download model weights.
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from vnvspec.core.protocols import ModelAdapter
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.torch.transformer import TransformerAdapter


@pytest.fixture(scope="module")
def adapter() -> TransformerAdapter:
    return TransformerAdapter(
        "prajjwal1/bert-tiny",
        device="cpu",
        sample_budget=10,
        batch_size=4,
    )


@pytest.fixture()
def sentiment_spec() -> Spec:
    return Spec(
        name="bert-sentiment",
        requirements=[
            Requirement(
                id="REQ-PROB",
                statement="The model shall produce probabilities in [0, 1].",
                rationale="Valid probability output.",
                verification_method="test",
                acceptance_criteria=["All probs in [0,1]."],
            ),
            Requirement(
                id="REQ-LABEL",
                statement="The model shall output label in {pos, neg}.",
                rationale="Binary classification.",
                verification_method="test",
                acceptance_criteria=["Output label in set."],
            ),
            Requirement(
                id="REQ-NONAN",
                statement="The model shall produce no NaN in logits.",
                rationale="Numerical stability.",
                verification_method="test",
                acceptance_criteria=["No NaN values."],
            ),
        ],
    )


@pytest.mark.slow()
class TestTransformerAdapter:
    def test_satisfies_protocol(self, adapter: TransformerAdapter) -> None:
        assert isinstance(adapter, ModelAdapter)

    def test_forward_single(self, adapter: TransformerAdapter) -> None:
        output = adapter.forward("This is a test sentence.")
        assert output.shape[0] == 1
        assert output.shape[1] == 2

    def test_forward_batch(self, adapter: TransformerAdapter) -> None:
        output = adapter.forward(["Hello world", "Another test"])
        assert output.shape[0] == 2

    def test_probabilities_valid(self, adapter: TransformerAdapter) -> None:
        output = adapter.forward("Test input")
        assert (output >= 0).all()
        assert (output <= 1).all()
        # Check probabilities sum to ~1
        assert torch.allclose(output.sum(dim=-1), torch.ones(1), atol=1e-5)

    def test_no_nan(self, adapter: TransformerAdapter) -> None:
        output = adapter.forward("Test input")
        assert not output.isnan().any()

    def test_describe(self, adapter: TransformerAdapter) -> None:
        desc = adapter.describe()
        assert desc["class"] == "TransformerAdapter"
        assert "bert-tiny" in desc["model_name"]
        assert desc["parameters"] > 0

    def test_assess(
        self,
        adapter: TransformerAdapter,
        sentiment_spec: Spec,
    ) -> None:
        data = [
            "I love this movie!",
            "This is terrible.",
            "Not bad at all.",
        ]
        report = adapter.assess(sentiment_spec, data)
        assert report.spec_name == "bert-sentiment"
        assert len(report.evidence) == 3
