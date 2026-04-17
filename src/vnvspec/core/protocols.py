"""Pluggability protocols for vnvspec.

Defines the :class:`ModelAdapter`, :class:`TestRunner`, and :class:`Exporter`
protocols that third-party integrations must satisfy. These are
:func:`~typing.runtime_checkable` so that conformance can be verified at
both type-check time (mypy) and runtime (isinstance).

Example:
    >>> from vnvspec.core.protocols import ModelAdapter
    >>> isinstance(object(), ModelAdapter)
    False
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from vnvspec.core.evidence import Evidence


@runtime_checkable
class ModelAdapter(Protocol):
    """Protocol for wrapping a model for assessment.

    Any class that implements these methods satisfies the protocol.

    Example:
        >>> class Dummy:
        ...     def forward(self, inputs, *, ctx=None): return inputs
        ...     def describe(self): return {}
        ...     def input_schema(self): return None
        ...     def output_schema(self): return None
        ...     def batch_size_hint(self): return 32
        ...     def supports_streaming(self): return False
        >>> isinstance(Dummy(), ModelAdapter)
        True
    """

    def forward(self, inputs: Any, *, ctx: Any = None) -> Any:
        """Run the model on the given inputs."""
        ...

    def describe(self) -> dict[str, Any]:
        """Return a description of the model."""
        ...

    def input_schema(self) -> dict[str, Any] | None:
        """Return the input schema, or None if unspecified."""
        ...

    def output_schema(self) -> dict[str, Any] | None:
        """Return the output schema, or None if unspecified."""
        ...

    def batch_size_hint(self) -> int:
        """Suggest a batch size for assessment."""
        ...

    def supports_streaming(self) -> bool:
        """Whether the adapter supports streaming outputs."""
        ...


@runtime_checkable
class TestRunner(Protocol):
    """Protocol for running tests against a spec and model.

    Example:
        >>> from vnvspec.core.protocols import TestRunner
        >>> isinstance(object(), TestRunner)
        False
    """

    def run(
        self,
        spec: Any,
        adapter: ModelAdapter,
        data: Any,
    ) -> list[Evidence]:
        """Run tests and return evidence."""
        ...


@runtime_checkable
class Exporter(Protocol):
    """Protocol for exporting reports.

    Example:
        >>> from vnvspec.core.protocols import Exporter
        >>> isinstance(object(), Exporter)
        False
    """

    def export(self, report: Any, path: Path, **kwargs: Any) -> Path:
        """Export a report to the given path."""
        ...
