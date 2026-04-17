"""Smoke tests for vnvspec package."""

import vnvspec


def test_version_is_string() -> None:
    """Package version is a non-empty string."""
    assert isinstance(vnvspec.__version__, str)
    assert len(vnvspec.__version__) > 0


def test_version_is_semver() -> None:
    """Package version follows semver (X.Y.Z) format."""
    parts = vnvspec.__version__.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)
