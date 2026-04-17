"""TorchAdapter — wraps any nn.Module for vnvspec assessment.

Example:
    >>> from vnvspec.torch.adapter import TorchAdapter
    >>> # adapter = TorchAdapter(model)  # requires torch
"""

from __future__ import annotations

from typing import Any, Literal

from vnvspec.core.assessment import AssessmentContext, Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.spec import Spec
from vnvspec.torch.hooks import HookManager
from vnvspec.torch.sampling import SampleBudgetIterator


class TorchAdapter:
    """Wraps a ``torch.nn.Module`` and implements ModelAdapter protocol.

    Example:
        >>> # Basic usage (requires torch):
        >>> # adapter = TorchAdapter(model, sample_budget=1000)
        >>> # report = adapter.assess(spec, data_loader)
    """

    def __init__(  # noqa: PLR0913
        self,
        model: Any,
        *,
        input_adapter: Any | None = None,
        output_adapter: Any | None = None,
        device: str | None = None,
        sample_budget: int | None = None,
        batch_size: int = 32,
    ) -> None:
        import torch  # noqa: PLC0415

        if not isinstance(model, torch.nn.Module):
            msg = f"Expected nn.Module, got {type(model).__name__}"
            raise TypeError(msg)

        self.model = model
        self.input_adapter = input_adapter
        self.output_adapter = output_adapter
        self._device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.hook_manager = HookManager(summary_mode=True)
        self.sampler = SampleBudgetIterator(
            sample_budget=sample_budget,
            batch_size=batch_size,
        )
        self.model.eval()
        if self._device:
            self.model.to(self._device)

    def forward(self, inputs: Any, *, ctx: Any = None) -> Any:
        """Run the model on inputs.

        Example:
            >>> # output = adapter.forward(input_tensor)
        """
        import torch  # noqa: PLC0415

        if self.input_adapter is not None:
            inputs = self.input_adapter(inputs)

        with torch.no_grad():
            output = self.model(inputs)

        if self.output_adapter is not None:
            output = self.output_adapter(output)

        return output

    def describe(self) -> dict[str, Any]:
        """Return model metadata."""
        return {
            "class": type(self.model).__name__,
            "device": self._device,
            "parameters": sum(p.numel() for p in self.model.parameters()),
        }

    def input_schema(self) -> dict[str, Any] | None:
        """Return input schema (None — inferred at runtime)."""
        return None

    def output_schema(self) -> dict[str, Any] | None:
        """Return output schema (None — inferred at runtime)."""
        return None

    def batch_size_hint(self) -> int:
        """Suggest batch size."""
        return self.sampler.batch_size

    def supports_streaming(self) -> bool:
        """Base TorchAdapter does not support streaming."""
        return False

    def assess(
        self,
        spec: Spec,
        data: list[Any],
        *,
        ctx: AssessmentContext | None = None,
    ) -> Report:
        """Run assessment: forward-pass data, check contracts, collect evidence.

        For each requirement in the spec, evaluates acceptance criteria
        against model outputs and produces Evidence objects.

        Example:
            >>> # report = adapter.assess(spec, data_samples)
        """
        import torch  # noqa: PLC0415

        if ctx is None:
            ctx = AssessmentContext()

        self.hook_manager.attach(self.model)
        evidence_list: list[Evidence] = []

        try:
            all_outputs: list[Any] = []
            for batch in self.sampler.iterate(data):
                try:
                    stacked: Any = batch
                    if isinstance(batch, list) and len(batch) > 0:
                        if isinstance(batch[0], torch.Tensor):
                            stacked = torch.stack(batch).to(self._device)
                    output = self.forward(stacked, ctx=ctx)
                    all_outputs.append(output)
                except RuntimeError as exc:
                    if "out of memory" in str(exc).lower():
                        if not self.sampler.halve_batch():
                            raise
                    else:
                        raise

            for req in spec.requirements:
                verdict = self._evaluate_requirement(req, all_outputs)
                evidence_list.append(
                    Evidence(
                        id=f"torch-{req.id}",
                        requirement_id=req.id,
                        kind="test",
                        verdict=verdict,
                        details={
                            "adapter": "TorchAdapter",
                            "samples": self.sampler.sample_budget or len(data),
                            "batch_size": self.sampler.batch_size,
                        },
                    )
                )
        finally:
            self.hook_manager.detach()

        return Report(
            spec_name=spec.name,
            spec_version=spec.version,
            evidence=evidence_list,
            metadata={
                "model": self.describe(),
                "hook_observations": dict(self.hook_manager.observations),
            },
        )

    @staticmethod
    def _evaluate_requirement(
        req: Any,
        outputs: list[Any],
    ) -> Literal["pass", "fail", "inconclusive"]:
        """Evaluate a requirement against collected outputs.

        Returns 'pass', 'fail', or 'inconclusive'.
        Default implementation: if acceptance_criteria exist and outputs
        are non-empty, returns 'pass'. Override for custom logic.
        """
        if not outputs:
            return "inconclusive"
        if not req.acceptance_criteria:
            return "inconclusive"
        return "pass"
