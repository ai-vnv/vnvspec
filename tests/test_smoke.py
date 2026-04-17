"""Smoke tests for vnvspec package."""

import vnvspec


def test_version_is_string() -> None:
    """Package version is a non-empty string."""
    assert isinstance(vnvspec.__version__, str)
    assert len(vnvspec.__version__) > 0


def test_version_value() -> None:
    """Package version matches expected value."""
    assert vnvspec.__version__ == "0.1.0"
