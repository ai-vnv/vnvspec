"""Offline tests for TransformerAdapter — no network access, no downloads.

Happy-path behavior runs against a tiny BERT classifier built locally
from a config with random weights (see the ``tiny_bert_dir`` fixture),
following the local-model pattern of tests/torch/test_adapter.py. The
loader fallback branches are exercised by substituting the transformers
factory classes with minimal stand-ins.

Complements tests/torch/test_transformer.py, whose end-to-end tests
download a pretrained checkpoint and are therefore marked slow; the
tests here are unmarked so they run in the standard CI coverage gate.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

torch = pytest.importorskip("torch")
# Gate only — deliberately not bound: see _current_transformers() for why a
# module-level transformers reference must not be used for monkeypatching.
pytest.importorskip("transformers")

from vnvspec.core.assessment import AssessmentContext
from vnvspec.core.protocols import ModelAdapter
from vnvspec.torch.transformer import TransformerAdapter

if TYPE_CHECKING:
    from pathlib import Path

    from vnvspec.core.spec import Spec


def _current_transformers() -> Any:
    """Return the live transformers module for monkeypatching.

    transformers 5.x replaces its entry in sys.modules during the first
    full ``from_pretrained`` load, so the module object imported at the
    top of this file can go stale. Patches must target the object that
    the adapter's own ``from transformers import ...`` will resolve.
    """
    import transformers as current

    return current


@pytest.fixture(scope="module")
def adapter(tiny_bert_dir: Path) -> TransformerAdapter:
    """Adapter wrapping the tiny local BERT classifier."""
    return TransformerAdapter(str(tiny_bert_dir), device="cpu", batch_size=4)


class TestTransformerAdapterOffline:
    """Behavioral tests against the tiny local model."""

    def test_satisfies_protocol(self, adapter: TransformerAdapter) -> None:
        """The adapter structurally satisfies the ModelAdapter protocol."""
        assert isinstance(adapter, ModelAdapter)

    def test_forward_single_string(self, adapter: TransformerAdapter) -> None:
        """A single string input produces one row of class probabilities."""
        output = adapter.forward("hello world")
        assert tuple(output.shape) == (1, 2)

    def test_forward_list_of_strings(self, adapter: TransformerAdapter) -> None:
        """A list input produces one probability row per string."""
        output = adapter.forward(["hello world", "a test input"])
        assert tuple(output.shape) == (2, 2)

    def test_forward_empty_string(self, adapter: TransformerAdapter) -> None:
        """An empty string still yields a valid probability row."""
        output = adapter.forward("")
        assert tuple(output.shape) == (1, 2)
        assert not output.isnan().any()

    def test_probabilities_are_valid(self, adapter: TransformerAdapter) -> None:
        """Outputs are probabilities: bounded, normalized, and NaN-free."""
        output = adapter.forward("this is a test")
        assert (output >= 0).all()
        assert (output <= 1).all()
        assert torch.allclose(output.sum(dim=-1), torch.ones(1), atol=1e-5)
        assert not output.isnan().any()

    def test_long_input_is_truncated(self, tiny_bert_dir: Path) -> None:
        """Inputs longer than max_length are truncated, not rejected.

        The input tokenizes to ~600 tokens, beyond the tiny model's 512
        position embeddings, so this forward pass can only succeed if the
        tokenizer actually truncates to max_length.
        """
        small = TransformerAdapter(str(tiny_bert_dir), device="cpu", max_length=16)
        output = small.forward("hello world " * 300)
        assert tuple(output.shape) == (1, 2)

    def test_describe(self, adapter: TransformerAdapter) -> None:
        """describe() reports class, device, limits, and parameter count."""
        desc = adapter.describe()
        assert desc["class"] == "TransformerAdapter"
        assert desc["device"] == "cpu"
        assert desc["max_length"] == 512
        assert desc["parameters"] > 0

    def test_schemas_and_hints(self, adapter: TransformerAdapter) -> None:
        """Schema and capability introspection match the adapter contract."""
        assert adapter.input_schema() == {"type": "list[str]", "max_length": 512}
        assert adapter.output_schema() == {"type": "tensor", "shape": "batch x num_labels"}
        assert adapter.batch_size_hint() == 4
        assert adapter.supports_streaming() is False


class TestTransformerAdapterAssess:
    """Assessment loop and default requirement evaluation."""

    def test_assess_produces_evidence_per_requirement(
        self, adapter: TransformerAdapter, adapter_spec: Spec
    ) -> None:
        """assess() yields one evidence item per requirement with correct verdicts."""
        report = adapter.assess(adapter_spec, ["hello", "a test input", "world"])
        assert report.spec_name == "adapter-offline-spec"
        assert len(report.evidence) == 2
        by_req = {e.requirement_id: e for e in report.evidence}
        assert by_req["REQ-PROB"].verdict == "pass"
        assert by_req["REQ-NOCRIT"].verdict == "inconclusive"
        assert by_req["REQ-PROB"].id == "transformer-REQ-PROB"
        assert by_req["REQ-PROB"].details["adapter"] == "TransformerAdapter"

    def test_assess_empty_data_is_inconclusive(
        self, adapter: TransformerAdapter, adapter_spec: Spec
    ) -> None:
        """With no data, every requirement is inconclusive."""
        report = adapter.assess(adapter_spec, [])
        assert len(report.evidence) == 2
        assert all(e.verdict == "inconclusive" for e in report.evidence)

    def test_assess_accepts_explicit_context(
        self, adapter: TransformerAdapter, adapter_spec: Spec
    ) -> None:
        """An explicit AssessmentContext is accepted (non-default branch)."""
        ctx = AssessmentContext(run_id="offline-run-001")
        report = adapter.assess(adapter_spec, ["hello"], ctx=ctx)
        assert report.spec_version == adapter_spec.version
        assert len(report.evidence) == 2


class _FakeTokenizer:
    """Sentinel tokenizer returned by stubbed loaders (identity-checked)."""


class _FakeModel:
    """Minimal model stand-in supporting the calls made in __init__."""

    def eval(self) -> _FakeModel:
        """Mirror nn.Module.eval()."""
        return self

    def to(self, device: str) -> _FakeModel:
        """Mirror nn.Module.to()."""
        return self


class TestTransformerAdapterLoaderFallbacks:
    """Loader fallback chains, forced via stubbed factory classes."""

    def test_tokenizer_fallback_to_bert_tokenizer(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AutoTokenizer failure falls back to BertTokenizer, in that order."""
        mod = _current_transformers()
        fake_tok = _FakeTokenizer()
        fake_model = _FakeModel()
        calls: list[str] = []

        class _FailingAutoTokenizer:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_tokenizer")
                raise ValueError("fast tokenizer unavailable")

        class _BertTokenizerStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("bert_tokenizer")
                return fake_tok

        class _AutoModelStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_model")
                return fake_model

        monkeypatch.setattr(mod, "AutoTokenizer", _FailingAutoTokenizer)
        monkeypatch.setattr(mod, "BertTokenizer", _BertTokenizerStub, raising=False)
        monkeypatch.setattr(mod, "AutoModelForSequenceClassification", _AutoModelStub)

        result = TransformerAdapter("stub-model", device="cpu")
        assert result.tokenizer is fake_tok
        assert result.model is fake_model
        assert calls == ["auto_tokenizer", "bert_tokenizer", "auto_model"]

    def test_tokenizer_fallback_to_slow_tokenizer(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When BertTokenizer also fails, the use_fast=False retry is used last."""
        mod = _current_transformers()
        fake_tok = _FakeTokenizer()
        fake_model = _FakeModel()
        calls: list[str] = []

        class _SlowOnlyAutoTokenizer:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                if kwargs.get("use_fast", True):
                    calls.append("auto_tokenizer_fast")
                    raise ValueError("fast tokenizer unavailable")
                calls.append("auto_tokenizer_slow")
                return fake_tok

        class _BrokenBertTokenizer:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("bert_tokenizer")
                raise RuntimeError("slow BERT tokenizer unavailable")

        class _AutoModelStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_model")
                return fake_model

        monkeypatch.setattr(mod, "AutoTokenizer", _SlowOnlyAutoTokenizer)
        monkeypatch.setattr(mod, "BertTokenizer", _BrokenBertTokenizer, raising=False)
        monkeypatch.setattr(mod, "AutoModelForSequenceClassification", _AutoModelStub)

        result = TransformerAdapter("stub-model", device="cpu")
        assert result.tokenizer is fake_tok
        assert calls == [
            "auto_tokenizer_fast",
            "bert_tokenizer",
            "auto_tokenizer_slow",
            "auto_model",
        ]

    def test_model_fallback_to_bert_classifier(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """AutoModel failure falls back to BertForSequenceClassification."""
        mod = _current_transformers()
        fake_tok = _FakeTokenizer()
        fake_model = _FakeModel()
        calls: list[str] = []

        class _AutoTokenizerStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_tokenizer")
                return fake_tok

        class _FailingAutoModel:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_model")
                raise OSError("model config lacks model_type")

        class _BertModelStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("bert_model")
                return fake_model

        monkeypatch.setattr(mod, "AutoTokenizer", _AutoTokenizerStub)
        monkeypatch.setattr(mod, "AutoModelForSequenceClassification", _FailingAutoModel)
        monkeypatch.setattr(mod, "BertForSequenceClassification", _BertModelStub, raising=False)

        result = TransformerAdapter("stub-model", device="cpu")
        assert result.tokenizer is fake_tok
        assert result.model is fake_model
        assert calls == ["auto_tokenizer", "auto_model", "bert_model"]
