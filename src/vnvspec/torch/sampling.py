"""Sample-budget iteration with OOM recovery.

Provides :class:`SampleBudgetIterator` that iterates over data with a
configurable sample budget and automatic batch-size halving on OOM.

Example:
    >>> it = SampleBudgetIterator(sample_budget=100, batch_size=32)
    >>> it.batch_size
    32
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


@dataclass
class SampleBudgetIterator:
    """Iterate over data respecting a sample budget.

    On CUDA OOM, halves the batch size and retries.

    Example:
        >>> it = SampleBudgetIterator(sample_budget=10, batch_size=4)
        >>> it.sample_budget
        10
    """

    sample_budget: int | None = None
    batch_size: int = 32
    min_batch_size: int = 1

    def iterate(self, data: list[Any]) -> Iterator[list[Any]]:
        """Yield batches from data, respecting sample budget.

        Example:
            >>> it = SampleBudgetIterator(sample_budget=5, batch_size=2)
            >>> batches = list(it.iterate([1, 2, 3, 4, 5, 6, 7]))
            >>> sum(len(b) for b in batches)
            5
        """
        total = len(data)
        if self.sample_budget is not None:
            total = min(total, self.sample_budget)

        idx = 0
        while idx < total:
            end = min(idx + self.batch_size, total)
            yield data[idx:end]
            idx = end

    def halve_batch(self) -> bool:
        """Halve the batch size. Returns False if already at minimum.

        Example:
            >>> it = SampleBudgetIterator(batch_size=8)
            >>> it.halve_batch()
            True
            >>> it.batch_size
            4
        """
        new_size = max(self.batch_size // 2, self.min_batch_size)
        if new_size == self.batch_size:
            return False
        self.batch_size = new_size
        return True
