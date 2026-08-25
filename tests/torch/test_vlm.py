"""Offline tests for VLMAdapter — no network access, no downloads.

Unlike the transformer and autoregressive suites, every test here runs
against recording stand-ins substituted at the transformers factory
seam: building a genuinely functional tiny vision-language model offline
(coordinated image processor + tokenizer + Vision2Seq weights) is the
most version-fragile artifact in the adapter family, while the adapter's
own testable value is its orchestration logic — item handling, processor
calls, device moves, decode aggregation.

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
from vnvspec.torch.vlm import VLMAdapter

if TYPE_CHECKING:
    from vnvspec.core.spec import Spec


def _live_transformers(transformers_module: Any) -> Any:
    """Stabilize the transformers module and return the live reference.

    The first resolution of ``AutoProcessor`` swaps
    sys.modules["transformers"] once per process (a stronger form of the
    staleness documented on the transformers_module fixture: even the
    getattr that monkeypatch performs to save an original can trigger
    it). Force that resolution first, then re-import, so patches land on
    the object the adapter's own ``import transformers`` will resolve.
    """
    getattr(transformers_module, "AutoProcessor", None)
    import transformers as live

    return live


class _RecordingProcessor:
    """Processor stand-in recording every encode and decode call."""

    def __init__(self) -> None:
        self.calls: list[tuple[Any, str]] = []
        self.encode_calls: list[dict[str, Any]] = []
        self.decode_calls: list[dict[str, Any]] = []

    def __call__(self, *, images: Any = None, text: str = "", **kwargs: Any) -> Any:
        """Record the (images, text) pair and remaining encode kwargs.

        Remaining kwargs are captured rather than defaulted so that an
        adapter regression dropping or altering ``return_tensors="pt"``
        fails the call-shape assertion instead of passing silently.

        The returned dict mixes tensors with a plain int so the adapter's
        hasattr(v, "to") device-move filter is exercised on both kinds.
        """
        self.calls.append((images, text))
        self.encode_calls.append(dict(kwargs))
        return {
            "input_ids": torch.ones((1, 3), dtype=torch.long),
            "pixel_values": torch.zeros((1, 2, 2)),
            "num_images": 1,
        }

    def batch_decode(self, output_ids: Any, **kwargs: Any) -> list[str]:
        """Record decode kwargs and return one caption per call."""
        self.decode_calls.append(dict(kwargs))
        return [f"caption-{len(self.decode_calls)}"]


class _RecordingVisionModel:
    """Vision2Seq model stand-in recording every generate() call."""

    def __init__(self) -> None:
        self.generate_calls: list[dict[str, Any]] = []

    def eval(self) -> _RecordingVisionModel:
        """Mirror nn.Module.eval()."""
        return self

    def to(self, device: str) -> _RecordingVisionModel:
        """Mirror nn.Module.to()."""
        return self

    def generate(self, **kwargs: Any) -> Any:
        """Record generation kwargs and return a fixed-size id tensor."""
        self.generate_calls.append(dict(kwargs))
        return torch.ones((1, 4), dtype=torch.long)

    def parameters(self) -> Any:
        """Mirror nn.Module.parameters() (used by describe())."""
        return iter([torch.zeros(4)])


def _adapter_with_stubs(
    monkeypatch: pytest.MonkeyPatch,
    transformers_module: Any,
    *,
    max_new_tokens: int,
) -> tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]:
    """Construct an adapter whose loaders return recording stand-ins."""
    processor = _RecordingProcessor()
    model = _RecordingVisionModel()
    live = _live_transformers(transformers_module)

    class _AutoProcessorStub:
        @classmethod
        def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
            return processor

    class _Vision2SeqStub:
        @classmethod
        def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
            return model

    monkeypatch.setattr(live, "AutoProcessor", _AutoProcessorStub)
    monkeypatch.setattr(live, "AutoModelForVision2Seq", _Vision2SeqStub, raising=False)
    adapter = VLMAdapter("stub-model", device="cpu", max_new_tokens=max_new_tokens)
    return adapter, processor, model


@pytest.fixture()
def stub_adapter(
    monkeypatch: pytest.MonkeyPatch, transformers_module: Any
) -> tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]:
    """Adapter wired to recording stand-ins, with max_new_tokens=6."""
    return _adapter_with_stubs(monkeypatch, transformers_module, max_new_tokens=6)


class TestVLMAdapterConstruction:
    """Loader wiring and the Vision2Seq/AutoModel fallback."""

    def test_loads_processor_then_vision_model(
        self, monkeypatch: pytest.MonkeyPatch, transformers_module: Any
    ) -> None:
        """AutoProcessor loads first, then AutoModelForVision2Seq."""
        live = _live_transformers(transformers_module)
        processor = _RecordingProcessor()
        model = _RecordingVisionModel()
        calls: list[str] = []

        class _AutoProcessorStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_processor")
                return processor

        class _Vision2SeqStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("vision2seq_model")
                return model

        monkeypatch.setattr(live, "AutoProcessor", _AutoProcessorStub)
        monkeypatch.setattr(live, "AutoModelForVision2Seq", _Vision2SeqStub, raising=False)

        adapter = VLMAdapter("stub-model", device="cpu")
        assert adapter.processor is processor
        assert adapter.model is model
        assert calls == ["auto_processor", "vision2seq_model"]

    def test_falls_back_to_automodel_when_vision2seq_missing(
        self, monkeypatch: pytest.MonkeyPatch, transformers_module: Any
    ) -> None:
        """Without AutoModelForVision2Seq, the AutoModel default is used."""
        live = _live_transformers(transformers_module)
        processor = _RecordingProcessor()
        model = _RecordingVisionModel()
        calls: list[str] = []

        class _AutoProcessorStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_processor")
                return processor

        class _AutoModelStub:
            @classmethod
            def from_pretrained(cls, name: str, **kwargs: Any) -> Any:
                calls.append("auto_model")
                return model

        monkeypatch.setattr(live, "AutoProcessor", _AutoProcessorStub)
        monkeypatch.delattr(live, "AutoModelForVision2Seq", raising=False)
        monkeypatch.setattr(live, "AutoModel", _AutoModelStub)

        adapter = VLMAdapter("stub-model", device="cpu")
        assert adapter.model is model
        assert calls == ["auto_processor", "auto_model"]

    def test_satisfies_protocol(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """The adapter structurally satisfies the ModelAdapter protocol."""
        adapter, _, _ = stub_adapter
        assert isinstance(adapter, ModelAdapter)


class TestVLMAdapterForward:
    """Multimodal input handling and generation flow."""

    def test_forward_single_dict(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """A single image+text dict yields one generated string."""
        adapter, processor, _ = stub_adapter
        image = torch.zeros(1, 3, 8, 8)
        output = adapter.forward({"images": image, "text": "describe this"})
        assert output == ["caption-1"]
        assert len(processor.calls) == 1
        assert processor.calls[0][0] is image
        assert processor.calls[0][1] == "describe this"

    def test_forward_list_of_dicts(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """A list of items is processed per item, outputs in order."""
        adapter, processor, _ = stub_adapter
        image = torch.zeros(1, 3, 8, 8)
        output = adapter.forward([{"images": image, "text": "a"}, {"images": image, "text": "b"}])
        assert output == ["caption-1", "caption-2"]
        assert [text for _, text in processor.calls] == ["a", "b"]

    def test_missing_text_defaults_to_empty(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """An item without a text key reaches the processor with ''."""
        adapter, processor, _ = stub_adapter
        adapter.forward({"images": torch.zeros(1, 3, 8, 8)})
        assert processor.calls[0][1] == ""

    def test_missing_images_passed_as_none(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """An item without an images key reaches the processor with None."""
        adapter, processor, _ = stub_adapter
        adapter.forward({"text": "text only"})
        assert processor.calls[0][0] is None

    def test_generation_parameters_passed_through(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """Generation receives the token budget and all processor outputs."""
        adapter, processor, model = stub_adapter
        adapter.forward({"images": torch.zeros(1, 3, 8, 8), "text": "hi"})
        assert processor.encode_calls == [{"return_tensors": "pt"}]
        generate_kwargs = model.generate_calls[0]
        assert generate_kwargs["max_new_tokens"] == 6
        # Non-tensor processor outputs must pass through the device-move
        # filter untouched; tensors must still be present.
        assert generate_kwargs["num_images"] == 1
        assert isinstance(generate_kwargs["input_ids"], torch.Tensor)
        assert isinstance(generate_kwargs["pixel_values"], torch.Tensor)
        assert processor.decode_calls == [{"skip_special_tokens": True}]


class TestVLMAdapterIntrospection:
    """Metadata, schema, and capability reporting."""

    def test_describe(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """describe() reports class, device, limits, and parameter count."""
        adapter, _, _ = stub_adapter
        desc = adapter.describe()
        assert desc["class"] == "VLMAdapter"
        assert desc["model_name"] == "stub-model"
        assert desc["device"] == "cpu"
        assert desc["max_new_tokens"] == 6
        assert desc["parameters"] == 4

    def test_schemas_and_hints(
        self, stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel]
    ) -> None:
        """Schema and capability introspection match the adapter contract."""
        adapter, _, _ = stub_adapter
        assert adapter.input_schema() == {"type": "list[dict]", "keys": ["images", "text"]}
        assert adapter.output_schema() == {"type": "list[str]"}
        assert adapter.batch_size_hint() == 4
        assert adapter.supports_streaming() is False


class TestVLMAdapterAssess:
    """Assessment loop and default requirement evaluation."""

    def test_assess_produces_evidence_per_requirement(
        self,
        stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel],
        adapter_spec: Spec,
    ) -> None:
        """assess() yields one evidence item per requirement with correct verdicts."""
        adapter, _, _ = stub_adapter
        image = torch.zeros(1, 3, 8, 8)
        data = [{"images": image, "text": f"item-{i}"} for i in range(3)]
        report = adapter.assess(adapter_spec, data)
        assert report.spec_name == "adapter-offline-spec"
        assert len(report.evidence) == 2
        by_req = {e.requirement_id: e for e in report.evidence}
        assert by_req["REQ-PROB"].verdict == "pass"
        assert by_req["REQ-NOCRIT"].verdict == "inconclusive"
        assert by_req["REQ-PROB"].id == "vlm-REQ-PROB"
        assert by_req["REQ-PROB"].details["adapter"] == "VLMAdapter"
        assert by_req["REQ-PROB"].details["generated_count"] == 3

    def test_assess_empty_data_is_inconclusive(
        self,
        stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel],
        adapter_spec: Spec,
    ) -> None:
        """With no data, every requirement is inconclusive."""
        adapter, _, _ = stub_adapter
        report = adapter.assess(adapter_spec, [])
        assert len(report.evidence) == 2
        assert all(e.verdict == "inconclusive" for e in report.evidence)
        assert all(e.details["generated_count"] == 0 for e in report.evidence)

    def test_assess_accepts_explicit_context(
        self,
        stub_adapter: tuple[VLMAdapter, _RecordingProcessor, _RecordingVisionModel],
        adapter_spec: Spec,
    ) -> None:
        """An explicit AssessmentContext is accepted (non-default branch)."""
        adapter, _, _ = stub_adapter
        ctx = AssessmentContext(run_id="offline-run-003")
        report = adapter.assess(adapter_spec, [{"text": "hi"}], ctx=ctx)
        assert report.spec_version == adapter_spec.version
        assert len(report.evidence) == 2
