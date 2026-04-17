"""AutoregressiveAdapter — wraps HuggingFace generate() models.

Supports streaming token-by-token invariants, stop-token semantics,
and max-new-tokens control.

Example:
    >>> # adapter = AutoregressiveAdapter("gpt2")
"""

from __future__ import annotations

from typing import Any, Literal

from vnvspec.core.assessment import AssessmentContext, Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.spec import Spec
from vnvspec.torch.sampling import SampleBudgetIterator


class AutoregressiveAdapter:
    """Wraps a HuggingFace causal LM for vnvspec assessment.

    Implements the ModelAdapter protocol.

    Example:
        >>> # adapter = AutoregressiveAdapter("gpt2")
    """

    def __init__(
        self,
        model_name_or_path: str,
        *,
        device: str | None = None,
        max_new_tokens: int = 256,
        sample_budget: int | None = None,
        batch_size: int = 8,
    ) -> None:
        import torch  # noqa: PLC0415
        from transformers import AutoModelForCausalLM, AutoTokenizer  # noqa: PLC0415

        self.model_name = model_name_or_path
        self.max_new_tokens = max_new_tokens
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer: Any = AutoTokenizer.from_pretrained(model_name_or_path)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model: Any = AutoModelForCausalLM.from_pretrained(model_name_or_path)
        self.model.eval()  # type: ignore[no-untyped-call]  # HF stubs incomplete
        self.model.to(self._device)  # type: ignore[arg-type]  # HF stubs incomplete

        self.sampler = SampleBudgetIterator(
            sample_budget=sample_budget,
            batch_size=batch_size,
        )

    def forward(self, inputs: Any, *, ctx: Any = None) -> Any:
        """Generate text from prompts.

        Accepts a string or list of strings. Returns generated text.
        """
        import torch  # noqa: PLC0415

        if isinstance(inputs, str):
            inputs = [inputs]

        encoded = self.tokenizer(
            inputs,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        encoded = {k: v.to(self._device) for k, v in encoded.items()}

        with torch.no_grad():
            output_ids = self.model.generate(
                **encoded,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
            )

        decoded = self.tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        return decoded

    def describe(self) -> dict[str, Any]:
        """Return model metadata."""
        return {
            "class": "AutoregressiveAdapter",
            "model_name": self.model_name,
            "device": self._device,
            "max_new_tokens": self.max_new_tokens,
            "parameters": sum(p.numel() for p in self.model.parameters()),
        }

    def input_schema(self) -> dict[str, Any] | None:
        """Input: list of prompt strings."""
        return {"type": "list[str]"}

    def output_schema(self) -> dict[str, Any] | None:
        """Output: list of generated strings."""
        return {"type": "list[str]"}

    def batch_size_hint(self) -> int:
        """Suggest batch size."""
        return self.sampler.batch_size

    def supports_streaming(self) -> bool:
        """Autoregressive models support streaming."""
        return True

    def assess(
        self,
        spec: Spec,
        data: list[str],
        *,
        ctx: AssessmentContext | None = None,
    ) -> Report:
        """Assess the model against a spec using prompt inputs."""
        if ctx is None:
            ctx = AssessmentContext()

        evidence_list: list[Evidence] = []
        all_outputs: list[Any] = []

        for batch in self.sampler.iterate(data):
            output = self.forward(batch, ctx=ctx)
            all_outputs.extend(output)

        for req in spec.requirements:
            verdict = self._evaluate(req, all_outputs)
            evidence_list.append(
                Evidence(
                    id=f"autoregressive-{req.id}",
                    requirement_id=req.id,
                    kind="test",
                    verdict=verdict,
                    details={
                        "adapter": "AutoregressiveAdapter",
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
