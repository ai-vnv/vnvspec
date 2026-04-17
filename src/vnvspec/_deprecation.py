"""Deprecation utilities for vnvspec.

Provides a decorator to mark functions, methods, or classes as deprecated
with a target removal version and suggested alternative.
"""

from __future__ import annotations

import functools
import warnings
from typing import Any, TypeVar

F = TypeVar("F")


def deprecated(version: str, alternative: str) -> Any:
    """Mark a callable as deprecated.

    Parameters
    ----------
    version:
        The version in which the symbol will be removed (e.g. ``"0.3.0"``).
    alternative:
        What users should use instead (e.g. ``"Spec.extend()"``)

    Example:
        >>> @deprecated("0.3.0", "new_function()")
        ... def old_function() -> str:
        ...     return "old"
        >>> import warnings
        >>> with warnings.catch_warnings(record=True) as w:
        ...     warnings.simplefilter("always")
        ...     old_function()
        ...     assert len(w) == 1
        ...     assert "deprecated" in str(w[0].message).lower()
        'old'
    """

    def decorator(fn: Any) -> Any:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{fn.__qualname__} is deprecated and will be removed in v{version}. "
                f"Use {alternative} instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return fn(*args, **kwargs)

        return wrapper

    return decorator
