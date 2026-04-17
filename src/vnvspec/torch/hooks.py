"""Forward-hook plumbing for PyTorch model inspection.

Installs forward hooks on ``nn.Module`` layers to observe inputs and outputs
during inference. By default, records summary statistics (shape, dtype, min,
max, mean, nan count) rather than full tensors to avoid OOM.

Example:
    >>> from vnvspec.torch.hooks import HookManager
    >>> hm = HookManager(summary_mode=True)
    >>> hm.summary_mode
    True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TensorSummary:
    """Summary statistics for an observed tensor.

    Example:
        >>> s = TensorSummary(shape=(3, 224, 224), dtype="float32")
        >>> s.shape
        (3, 224, 224)
    """

    shape: tuple[int, ...] = ()
    dtype: str = ""
    min_val: float | None = None
    max_val: float | None = None
    mean_val: float | None = None
    nan_count: int = 0


@dataclass
class HookManager:
    """Manages forward hooks for model inspection.

    Example:
        >>> hm = HookManager()
        >>> hm.summary_mode
        True
    """

    summary_mode: bool = True
    observations: dict[str, list[TensorSummary]] = field(
        default_factory=dict,
    )
    _handles: list[Any] = field(default_factory=list)

    def _make_hook(self, layer_name: str) -> Any:
        """Create a forward hook closure for a named layer."""
        import torch  # noqa: PLC0415

        def hook(
            _module: torch.nn.Module,
            _input: Any,
            output: Any,
        ) -> None:
            if isinstance(output, torch.Tensor):
                summary = TensorSummary(
                    shape=tuple(output.shape),
                    dtype=str(output.dtype),
                    min_val=float(output.min()),
                    max_val=float(output.max()),
                    mean_val=float(output.float().mean()),
                    nan_count=int(output.isnan().sum()),
                )
                self.observations.setdefault(layer_name, []).append(summary)

        return hook

    def attach(self, model: Any, layer_names: list[str] | None = None) -> None:
        """Attach forward hooks to the model.

        If ``layer_names`` is None, attaches to all named children.

        Example:
            >>> hm = HookManager()
            >>> hm.observations
            {}
        """
        import torch  # noqa: PLC0415

        if not isinstance(model, torch.nn.Module):
            msg = f"Expected nn.Module, got {type(model).__name__}"
            raise TypeError(msg)

        targets: list[tuple[str, Any]] = []
        if layer_names is not None:
            named = dict(model.named_modules())
            for name in layer_names:
                if name in named:
                    targets.append((name, named[name]))
        else:
            targets = list(model.named_children())

        for name, module in targets:
            handle = module.register_forward_hook(self._make_hook(name))
            self._handles.append(handle)

    def detach(self) -> None:
        """Remove all registered hooks."""
        for handle in self._handles:
            handle.remove()
        self._handles.clear()

    def clear(self) -> None:
        """Clear observations without removing hooks."""
        self.observations.clear()
