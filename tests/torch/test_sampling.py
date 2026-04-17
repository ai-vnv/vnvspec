"""Tests for sample-budget iterator (no torch dependency)."""

from __future__ import annotations

from vnvspec.torch.sampling import SampleBudgetIterator


class TestSampleBudgetIterator:
    def test_basic_iteration(self) -> None:
        it = SampleBudgetIterator(batch_size=3)
        data = list(range(10))
        batches = list(it.iterate(data))
        flat = [x for b in batches for x in b]
        assert flat == data

    def test_with_budget(self) -> None:
        it = SampleBudgetIterator(sample_budget=5, batch_size=2)
        data = list(range(10))
        batches = list(it.iterate(data))
        total = sum(len(b) for b in batches)
        assert total == 5

    def test_budget_larger_than_data(self) -> None:
        it = SampleBudgetIterator(sample_budget=100, batch_size=4)
        data = list(range(7))
        batches = list(it.iterate(data))
        total = sum(len(b) for b in batches)
        assert total == 7

    def test_halve_batch(self) -> None:
        it = SampleBudgetIterator(batch_size=16)
        assert it.halve_batch() is True
        assert it.batch_size == 8
        assert it.halve_batch() is True
        assert it.batch_size == 4

    def test_halve_at_minimum(self) -> None:
        it = SampleBudgetIterator(batch_size=1, min_batch_size=1)
        assert it.halve_batch() is False
        assert it.batch_size == 1

    def test_empty_data(self) -> None:
        it = SampleBudgetIterator(batch_size=4)
        batches = list(it.iterate([]))
        assert batches == []
