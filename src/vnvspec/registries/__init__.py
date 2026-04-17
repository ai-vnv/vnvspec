"""Standards registries for vnvspec.

Provides access to versioned clause databases for international standards
such as ISO/PAS 8800, ISO 21448, UL 4600, EU AI Act, and NIST AI RMF.

Example:
    >>> from vnvspec.registries import load, list_available
    >>> names = list_available()
    >>> len(names) >= 5
    True
"""

from vnvspec.registries.loader import (
    Registry,
    RegistryEntry,
    RegistryError,
    list_available,
    load,
)

__all__ = [
    "Registry",
    "RegistryEntry",
    "RegistryError",
    "list_available",
    "load",
]
