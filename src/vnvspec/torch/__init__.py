"""PyTorch adapter for vnvspec.

Provides :class:`TorchAdapter` that wraps any ``torch.nn.Module``
and implements the :class:`~vnvspec.core.protocols.ModelAdapter` protocol.

This module requires ``torch`` to be installed: ``pip install vnvspec[torch]``.
"""

from vnvspec.torch.adapter import TorchAdapter
from vnvspec.torch.hooks import HookManager
from vnvspec.torch.sampling import SampleBudgetIterator

__all__ = [
    "HookManager",
    "SampleBudgetIterator",
    "TorchAdapter",
]
