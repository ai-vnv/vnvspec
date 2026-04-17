"""Registry loader — loads standards clause databases from bundled JSON.

Example:
    >>> registry = load("iso_pas_8800")
    >>> registry.name
    'ISO/PAS 8800'
    >>> len(registry.entries) >= 30
    True
"""

from __future__ import annotations

import json
from importlib import resources
from typing import Any, Literal

from pydantic import BaseModel, Field

from vnvspec.core.errors import VnvspecError

NormativeLevel = Literal["shall", "should", "may", "informative"]


class RegistryError(VnvspecError):
    """Raised when a registry operation fails.

    Example:
        >>> raise RegistryError("not found")
        Traceback (most recent call last):
            ...
        vnvspec.registries.loader.RegistryError: not found
    """

    help_url: str = "https://vnvspec.dev/standards/"


class RegistryEntry(BaseModel):
    """A single clause entry in a standards registry.

    Example:
        >>> entry = RegistryEntry(
        ...     id="8800-6.2.1",
        ...     clause="6.2.1",
        ...     title="Safety goals",
        ...     summary="Define safety goals derived from HARA.",
        ...     normative_level="shall",
        ... )
        >>> entry.clause
        '6.2.1'
    """

    model_config = {"frozen": True}

    id: str = Field(description="Unique entry identifier within the registry.")
    clause: str = Field(description="Clause number, e.g. '6.2.1'.")
    title: str = Field(description="Clause title.")
    summary: str = Field(default="", description="Brief summary of the clause.")
    parent: str = Field(
        default="",
        description="Parent clause id for hierarchical navigation.",
    )
    normative_level: NormativeLevel = Field(
        default="informative",
        description="Normative level: shall, should, may, or informative.",
    )
    source_edition: str = Field(
        default="",
        description="Edition or version of the source standard.",
    )


class Registry(BaseModel):
    """A complete standards registry with metadata and entries.

    Example:
        >>> r = Registry(name="Test", version="1.0", entries=[])
        >>> r.name
        'Test'
    """

    model_config = {"frozen": True}

    name: str = Field(description="Human-readable standard name.")
    version: str = Field(default="", description="Registry version.")
    published: str = Field(default="", description="Publication date.")
    url: str = Field(default="", description="URL to the standard.")
    disclaimer: str = Field(
        default=("Informative only. Not a substitute for reading the published standard."),
        description="Legal disclaimer.",
    )
    entries: list[RegistryEntry] = Field(
        default_factory=list, description="List of clause entries."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional registry metadata.",
    )


def _data_path() -> resources.abc.Traversable:
    """Return the path to the bundled data directory."""
    return resources.files("vnvspec.registries") / "data"


def list_available() -> list[str]:
    """List all available registry names.

    Returns sorted list of registry identifiers (without .json extension).

    Example:
        >>> names = list_available()
        >>> "iso_pas_8800" in names
        True
    """
    data_dir = _data_path()
    names: list[str] = []
    for item in data_dir.iterdir():
        name = str(item).rsplit("/", maxsplit=1)[-1]
        if name.endswith(".json"):
            names.append(name.removesuffix(".json"))
    return sorted(names)


def load(name: str) -> Registry:
    """Load a registry by name.

    Raises :class:`RegistryError` if the registry is not found.

    Example:
        >>> r = load("iso_pas_8800")
        >>> r.name
        'ISO/PAS 8800'
    """
    data_dir = _data_path()
    path = data_dir / f"{name}.json"
    try:
        raw = path.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError) as exc:
        available = list_available()
        raise RegistryError(f"Registry '{name}' not found. Available: {available}") from exc
    data = json.loads(raw)
    return Registry.model_validate(data)


def list_clauses(name: str) -> list[str]:
    """Return all clause numbers in a registry.

    Example:
        >>> clauses = list_clauses("iso_pas_8800")
        >>> len(clauses) >= 30
        True
    """
    registry = load(name)
    return [e.clause for e in registry.entries]
