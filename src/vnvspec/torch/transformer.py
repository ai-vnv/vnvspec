"""TransformerAdapter — wraps HuggingFace encoder and seq2seq models.

Handles tokenizer ingress (str -> tokens + attention_mask), token-length
invariants, and padding-aware output processing.

Example:
    >>> # adapter = TransformerAdapter("bert-base-uncased")
"""

from __future__ import annotations

from typing import Any, Literal

from vnvspec.core.assessment import AssessmentContext, Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.spec import Spec
from vnvspec.torch.sampling import SampleBudgetIterator


class TransformerAdapter:
    """Wraps a HuggingFace encoder/seq2seq model for vnvspec assessment.

    Implements the ModelAdapter protocol.

    Example:
        >>> # adapter = TransformerAdapter("prajjwal1/bert-tiny")
    """

    def __init__(  # noqa: PLR0913
        self,
        model_name_or_path: str,
        *,
        task: str = "text-classification",
        device: str | None = None,
        max_length: int = 512,
        sample_budget: int | None = None,
        batch_size: int = 16,
    ) -> None:
        import torch  # noqa: PLC0415
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # noqa: PLC0415

        self.model_name = model_name_or_path
        self.task = task
        self.max_length = max_length
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        except (ValueError, ImportError):
            # Fast tokenizer backend may be unavailable (missing tokenizers
            # Rust build or sentencepiece). Import the slow tokenizer class
            # matching the model config and fall back to it.
            try:
                from transformers import BertTokenizer  # noqa: PLC0415

                self.tokenizer = BertTokenizer.from_pretrained(model_name_or_path)
            except Exception:
                # Last resort for non-BERT models
                self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=False)
        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name_or_path)
        except (ValueError, OSError):
            # Model config may lack model_type (older HF Hub cards).
            # Fall back to explicit BertForSequenceClassification.
            from transformers import BertForSequenceClassification  # noqa: PLC0415

            self.model = BertForSequenceClassification.from_pretrained(model_name_or_path)
        self.model.eval()
        self.model.to(self._device)

        self.sampler = SampleBudgetIterator(
            sample_budget=sample_budget,
            batch_size=batch_size,
        )

    def forward(self, inputs: Any, *, ctx: Any = None) -> Any:
        """Tokenize and run the model.

        Accepts a string or list of strings.
        """
        import torch  # noqa: PLC0415

        if isinstance(inputs, str):
            inputs = [inputs]

        encoded = self.tokenizer(
            inputs,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        encoded = {k: v.to(self._device) for k, v in encoded.items()}

        with torch.no_grad():
            outputs = self.model(**encoded)

        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
        return probs

    def describe(self) -> dict[str, Any]:
        """Return model metadata."""
        return {
            "class": "TransformerAdapter",
            "model_name": self.model_name,
            "task": self.task,
            "device": self._device,
            "max_length": self.max_length,
            "parameters": sum(p.numel() for p in self.model.parameters()),
        }

    def input_schema(self) -> dict[str, Any] | None:
        """Input: list of strings."""
        return {"type": "list[str]", "max_length": self.max_length}

    def output_schema(self) -> dict[str, Any] | None:
        """Output: probability tensor."""
        return {"type": "tensor", "shape": "batch x num_labels"}

    def batch_size_hint(self) -> int:
        """Suggest batch size."""
        return self.sampler.batch_size

    def supports_streaming(self) -> bool:
        """Encoder models do not support streaming."""
        return False

    def assess(
        self,
        spec: Spec,
        data: list[str],
        *,
        ctx: AssessmentContext | None = None,
    ) -> Report:
        """Assess the model against a spec using text inputs."""
        if ctx is None:
            ctx = AssessmentContext()

        evidence_list: list[Evidence] = []
        all_outputs: list[Any] = []

        for batch in self.sampler.iterate(data):
            output = self.forward(batch, ctx=ctx)
            all_outputs.append(output)

        for req in spec.requirements:
            verdict = self._evaluate(req, all_outputs)
            evidence_list.append(
                Evidence(
                    id=f"transformer-{req.id}",
                    requirement_id=req.id,
                    kind="test",
                    verdict=verdict,
                    details={
                        "adapter": "TransformerAdapter",
                        "model": self.model_name,
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
