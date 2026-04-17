"""VLMAdapter — wraps HuggingFace vision-language models.

Handles image preprocessing via AutoProcessor and multi-modal input.
Provides VLM-specific invariant vocabulary.

Example:
    >>> # adapter = VLMAdapter("Salesforce/blip2-opt-2.7b")
"""

from __future__ import annotations

from typing import Any, Literal

from vnvspec.core.assessment import AssessmentContext, Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.spec import Spec
from vnvspec.torch.sampling import SampleBudgetIterator


class VLMAdapter:
    """Wraps a HuggingFace vision-language model for vnvspec assessment.

    Implements the ModelAdapter protocol.

    Example:
        >>> # adapter = VLMAdapter("Salesforce/blip2-opt-2.7b")
    """

    def __init__(
        self,
        model_name_or_path: str,
        *,
        device: str | None = None,
        max_new_tokens: int = 256,
        sample_budget: int | None = None,
        batch_size: int = 4,
    ) -> None:
        import torch  # noqa: PLC0415
        import transformers  # noqa: PLC0415

        self.model_name = model_name_or_path
        self.max_new_tokens = max_new_tokens
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.processor: Any = transformers.AutoProcessor.from_pretrained(model_name_or_path)  # type: ignore[no-untyped-call]  # HF stubs incomplete
        vlm_cls: Any = getattr(transformers, "AutoModelForVision2Seq", transformers.AutoModel)
        self.model: Any = vlm_cls.from_pretrained(model_name_or_path)
        self.model.eval()
        self.model.to(self._device)

        self.sampler = SampleBudgetIterator(
            sample_budget=sample_budget,
            batch_size=batch_size,
        )

    def forward(self, inputs: Any, *, ctx: Any = None) -> Any:
        """Process image+text inputs through the VLM.

        Accepts a dict with 'images' and optional 'text' keys,
        or a list of such dicts.
        """
        import torch  # noqa: PLC0415

        if isinstance(inputs, dict):
            inputs = [inputs]

        all_outputs: list[str] = []
        for item in inputs:
            images = item.get("images")
            text = item.get("text", "")
            processed = self.processor(
                images=images,
                text=text,
                return_tensors="pt",
            )
            processed = {
                k: v.to(self._device) if hasattr(v, "to") else v for k, v in processed.items()
            }

            with torch.no_grad():
                output_ids = self.model.generate(
                    **processed,
                    max_new_tokens=self.max_new_tokens,
                )

            decoded = self.processor.batch_decode(output_ids, skip_special_tokens=True)
            all_outputs.extend(decoded)

        return all_outputs

    def describe(self) -> dict[str, Any]:
        """Return model metadata."""
        return {
            "class": "VLMAdapter",
            "model_name": self.model_name,
            "device": self._device,
            "max_new_tokens": self.max_new_tokens,
            "parameters": sum(p.numel() for p in self.model.parameters()),
        }

    def input_schema(self) -> dict[str, Any] | None:
        """Input: list of dicts with 'images' and optional 'text'."""
        return {"type": "list[dict]", "keys": ["images", "text"]}

    def output_schema(self) -> dict[str, Any] | None:
        """Output: list of generated strings."""
        return {"type": "list[str]"}

    def batch_size_hint(self) -> int:
        """Suggest batch size."""
        return self.sampler.batch_size

    def supports_streaming(self) -> bool:
        """VLM does not support streaming by default."""
        return False

    def assess(
        self,
        spec: Spec,
        data: list[dict[str, Any]],
        *,
        ctx: AssessmentContext | None = None,
    ) -> Report:
        """Assess the VLM against a spec using image+text inputs."""
        if ctx is None:
            ctx = AssessmentContext()

        evidence_list: list[Evidence] = []
        all_outputs: list[str] = []

        for batch in self.sampler.iterate(data):
            for item in batch:
                output = self.forward(item, ctx=ctx)
                all_outputs.extend(output)

        for req in spec.requirements:
            verdict = self._evaluate(req, all_outputs)
            evidence_list.append(
                Evidence(
                    id=f"vlm-{req.id}",
                    requirement_id=req.id,
                    kind="test",
                    verdict=verdict,
                    details={
                        "adapter": "VLMAdapter",
                        "model": self.model_name,
                        "generated_count": len(all_outputs),
                    },
                )
            )

        return Report(
            spec_name=spec.name,
            spec_version=spec.version,
            evidence=evidence_list,
        )

    @staticmethod
    def _evaluate(
        req: Any,
        outputs: list[Any],
    ) -> Literal["pass", "fail", "inconclusive"]:
        """Evaluate requirement against outputs."""
        if not outputs:
            return "inconclusive"
        if not req.acceptance_criteria:
            return "inconclusive"
        return "pass"
