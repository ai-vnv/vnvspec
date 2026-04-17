"""Tests for the deprecation infrastructure."""

from __future__ import annotations

import warnings

import pytest

from vnvspec._deprecation import deprecated


class TestDeprecated:
    @pytest.mark.vnvspec("REQ-SELF-DEP-001")
    def test_emits_deprecation_warning(self) -> None:
        @deprecated("0.3.0", "new_func()")
        def old_func() -> str:
            return "value"

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = old_func()

        assert result == "value"
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "deprecated" in str(w[0].message).lower()
        assert "0.3.0" in str(w[0].message)
        assert "new_func()" in str(w[0].message)

    def test_preserves_function_name(self) -> None:
        @deprecated("0.3.0", "other()")
        def my_function() -> None:
            pass

        assert my_function.__name__ == "my_function"

    def test_passes_arguments(self) -> None:
        @deprecated("0.3.0", "new_add()")
        def old_add(a: int, b: int) -> int:
            return a + b

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            assert old_add(2, 3) == 5
