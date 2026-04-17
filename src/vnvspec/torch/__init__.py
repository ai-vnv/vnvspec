"""PyTorch adapter for vnvspec.

Provides adapters that wrap PyTorch and HuggingFace models
and implement the :class:`~vnvspec.core.protocols.ModelAdapter` protocol.

This module requires ``torch`` to be installed: ``pip install vnvspec[torch]``.
"""

from vnvspec.torch.adapter import TorchAdapter
from vnvspec.torch.autoregressive import AutoregressiveAdapter
from vnvspec.torch.hooks import HookManager
from vnvspec.torch.sampling import SampleBudgetIterator
from vnvspec.torch.transformer import TransformerAdapter
from vnvspec.torch.vlm import VLMAdapter

__all__ = [
    "AutoregressiveAdapter",
    "HookManager",
    "SampleBudgetIterator",
    "TorchAdapter",
    "TransformerAdapter",
    "VLMAdapter",
]
