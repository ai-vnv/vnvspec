"""Offline tests for AutoregressiveAdapter — no network access, no downloads.

Happy-path behavior runs against a tiny GPT-2 causal LM built locally
from a config with random weights (see the ``tiny_gpt2_dir`` fixture),
following the local-model pattern of tests/torch/test_adapter.py. The
generation-parameter contract (greedy decoding, max_new_tokens, special
token handling) is pinned with recording stand-ins substituted at the
transformers factory seam.

Complements the structural checks in tests/torch/test_hf_adapters.py;
the tests here are unmarked so they run in the standard CI coverage gate.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

torch = pytest.importorskip("torch")
# Gate only — deliberately not bound: see the transformers_module fixture
# for why a module-level transformers reference must not be used for
# monkeypatching.
pytest.importorskip("transformers")

from vnvspec.core.assessment import AssessmentContext
from vnvspec.core.protocols import ModelAdapter
from vnvspec.torch.autoregressive import AutoregressiveAdapter

if TYPE_CHECKING:
    from pathlib import Path

    from vnvspec.core.spec import Spec


@pytest.fixture(scope="module")
def adapter(tiny_gpt2_dir: Path) -> AutoregressiveAdapter:
    """Adapter wrapping the tiny local GPT-2 causal LM."""
    return AutoregressiveAdapter(str(tiny_gpt2_dir), device="cpu", max_new_tokens=4, batch_size=2)


class TestAutoregressiveAdapterOffline:
    """Behavioral tests against the tiny local model."""

    def test_satisfies_protocol(self, adapter: AutoregressiveAdapter) -> None:
        """The adapter structurally satisfies the ModelAdapter protocol."""
        assert isinstance(adapter, ModelAdapter)

    def test_forward_single_string(self, adapter: AutoregressiveAdapter) -> None:
        """A single prompt yields a one-element list of generated strings."""
        output = adapter.forward("hello world")
        assert isinstance(output, list)
        assert len(output) == 1
        assert isinstance(output[0], str)
        assert output[0].startswith("hello world")

    def test_forward_list_of_strings(self, adapter: AutoregressiveAdapter) -> None:
        """A list of prompts yields one generation per prompt, in order."""
        output = adapter.forward(["hello world", "world hello"])
        assert len(output) == 2
        assert output[0].startswith("hello world")
        assert output[1].startswith("world hello")

    def test_generation_is_deterministic(self, adapter: AutoregressiveAdapter) -> None:
        """Greedy decoding (do_sample=False) is reproducible run-to-run."""
        first = adapter.forward("hello world")
        second = adapter.forward("hello world")
        assert first == second

    def test_missing_pad_token_defaults_to_eos(self, adapter: AutoregressiveAdapter) -> None:
        """GPT-2 has no pad token; the adapter must default it to eos."""
        assert adapter.tokenizer.pad_token is not None
        assert adapter.tokenizer.pad_token == adapter.tokenizer.eos_token

    def test_describe(self, adapter: AutoregressiveAdapter) -> None:
        """describe() reports class, device, limits, and parameter count."""
        desc = adapter.describe()
        assert desc["class"] == "AutoregressiveAdapter"
        assert desc["device"] == "cpu"
        assert desc["max_new_tokens"] == 4
        assert desc["parameters"] > 0

    def test_schemas_and_hints(self, adapter: AutoregressiveAdapter) -> None:
        """Schema and capability introspection match the adapter contract."""
        assert adapter.input_schema() == {"type": "list[str]"}
        assert adapter.output_schema() == {"type": "list[str]"}
        assert adapter.batch_size_hint() == 2
        assert adapter.supports_streaming() is True


class TestAutoregressiveAdapterAssess:
    """Assessment loop and default requirement evaluation."""

    def test_assess_produces_evidence_per_requirement(
        self, adapter: AutoregressiveAdapter, adapter_spec: Spec
    ) -> None:
        """assess() yields one evidence item per requirement with correct verdicts."""
        report = adapter.assess(adapter_spec, ["hello", "hello world", "world"])
        assert report.spec_name == "adapter-offline-spec"
        assert len(report.evidence) == 2
        by_req = {e.requirement_id: e for e in report.evidence}
        assert by_req["REQ-PROB"].verdict == "pass"
        assert by_req["REQ-NOCRIT"].verdict == "inconclusive"
        assert by_req["REQ-PROB"].id == "autoregressive-REQ-PROB"
        assert by_req["REQ-PROB"].details["adapter"] == "AutoregressiveAdapter"
        assert by_req["REQ-PROB"].details["generated_count"] == 3

    def test_assess_empty_data_is_inconclusive(
        self, adapter: AutoregressiveAdapter, adapter_spec: Spec
    ) -> None:
        """With no data, every requirement is inconclusive."""
        report = adapter.assess(adapter_spec, [])
        assert len(report.evidence) == 2
        assert all(e.verdict == "inconclusive" for e in report.evidence)
        assert all(e.details["generated_count"] == 0 for e in report.evidence)

    def test_assess_accepts_explicit_context(
        self, adapter: AutoregressiveAdapter, adapter_spec: Spec
    ) -> None:
        """An explicit AssessmentContext is accepted (non-default branch)."""
        ctx = AssessmentContext(run_id="offline-run-002")
        report = adapter.assess(adapter_spec, ["hello"], ctx=ctx)
        assert report.spec_version == adapter_spec.version
        assert len(report.evidence) == 2


class _RecordingTokenizer:
    """Tokenizer stand-in recording decode kwargs; pad/eos configurable."""

    def __init__(self, *, pad_token: str | None) -> None:
        self.pad_token = pad_token
        self.eos_token = "<eos>"
        self.encode_kwargs: dict[str, Any] = {}
        self.decode_kwargs: dict[str, Any] = {}

    def __call__(self, inputs: list[str], **kwargs: Any) -> dict[str, Any]:
        """Record encode kwargs and mirror batch encoding with fixed-shape tensors."""
        self.encode_kwargs = dict(kwargs)
        batch = len(inputs)
        return {
            "input_ids": torch.ones((batch, 3), dtype=torch.long),
            "attention_mask": torch.ones((batch, 3), dtype=torch.long),
        }

    def batch_decode(self, output_ids: Any, **kwargs: Any) -> list[str]:
        """Record decode kwargs and return one string per row."""
        self.decode_kwargs = dict(kwargs)
        return [f"decoded-{i}" for i in range(output_ids.shape[0])]


class _RecordingCausalLM:
    """Causal LM stand-in recording generate() kwargs."""

    def __init__(self) -> None:
        self.generate_kwargs: dict[str, Any] = {}

    def eval(self) -> _RecordingCausalLM:
        """Mirror nn.Module.eval()."""
        return self

    def to(self, device: str) -> _RecordingCausalLM:
        """Mirror nn.Module.to()."""
        return self

    def generate(self, **kwargs: Any) -> Any:
        """Record generation kwargs and return a fixed-size id tensor."""
        self.generate_kwargs = dict(kwargs)
        input_ids = kwargs["input_ids"]
        return torch.ones((input_ids.shape[0], 5), dtype=torch.long)


def _adapter_with_stubs(
    monkeypatch: pytest.MonkeyPatch,
    transformers_module: Any,
    *,
    pad_token: str | None,
) -> tuple[AutoregressiveAdapter, _RecordingTokenizer, _RecordingCausalLM]:
    """Construct an adapter whose loaders return recording stand-ins."""
    tokenizer = _RecordingTokenizer(pad_token=pad_token)
    model = _RecordingCausalLM()

    class _AutoTokenizerStub:
        @classmethod
        def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
            return tokenizer

    class _AutoModelStub:
        @classmethod
        def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
            return model

    monkeypatch.setattr(transformers_module, "AutoTokenizer", _AutoTokenizerStub)
    monkeypatch.setattr(transformers_module, "AutoModelForCausalLM", _AutoModelStub)
    adapter = AutoregressiveAdapter("stub-model", device="cpu", max_new_tokens=7)
    return adapter, tokenizer, model


class TestAutoregressiveGenerationContract:
    """Generation-parameter contract, pinned via recording stand-ins."""

    def test_generation_parameters_passed_through(
        self, monkeypatch: pytest.MonkeyPatch, transformers_module: Any
    ) -> None:
        """forward() generates greedily with the configured token budget."""
        adapter, tokenizer, model = _adapter_with_stubs(
            monkeypatch, transformers_module, pad_token="<pad>"
        )
        output = adapter.forward(["a", "b"])
        assert tokenizer.encode_kwargs["padding"] is True
        assert tokenizer.encode_kwargs["truncation"] is True
        assert model.generate_kwargs["max_new_tokens"] == 7
        assert model.generate_kwargs["do_sample"] is False
        assert tokenizer.decode_kwargs == {"skip_special_tokens": True}
        assert output == ["decoded-0", "decoded-1"]

    def test_missing_pad_token_replaced_with_eos(
        self, monkeypatch: pytest.MonkeyPatch, transformers_module: Any
    ) -> None:
        """A tokenizer without a pad token gets eos assigned at init."""
        adapter, tokenizer, _ = _adapter_with_stubs(
            monkeypatch, transformers_module, pad_token=None
        )
        assert tokenizer.pad_token == "<eos>"
        assert adapter.tokenizer is tokenizer

    def test_existing_pad_token_preserved(
        self, monkeypatch: pytest.MonkeyPatch, transformers_module: Any
    ) -> None:
        """A tokenizer that already has a pad token is left untouched."""
        _, tokenizer, _ = _adapter_with_stubs(monkeypatch, transformers_module, pad_token="<pad>")
        assert tokenizer.pad_token == "<pad>"
