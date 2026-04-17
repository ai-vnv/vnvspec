"""Structural tests for AutoregressiveAdapter and VLMAdapter.

These tests verify the adapter classes can be imported and
have the correct interface, without loading actual models.
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")

from vnvspec.torch.autoregressive import AutoregressiveAdapter
from vnvspec.torch.vlm import VLMAdapter


class TestAutoregressiveAdapterStructure:
    def test_class_exists(self) -> None:
        assert AutoregressiveAdapter is not None

    def test_has_required_methods(self) -> None:
        methods = [
            "forward",
            "describe",
            "input_schema",
            "output_schema",
            "batch_size_hint",
            "supports_streaming",
            "assess",
        ]
        for method in methods:
            assert hasattr(AutoregressiveAdapter, method)


class TestVLMAdapterStructure:
    def test_class_exists(self) -> None:
        assert VLMAdapter is not None

    def test_has_required_methods(self) -> None:
        methods = [
            "forward",
            "describe",
            "input_schema",
            "output_schema",
            "batch_size_hint",
            "supports_streaming",
            "assess",
        ]
        for method in methods:
            assert hasattr(VLMAdapter, method)
