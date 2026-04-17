"""Demo catalog. Returns trivial requirements to validate the catalog convention.

This is NOT a real best-practices catalog. Real catalogs ship in v0.3.
See: https://ai-vnv.github.io/vnvspec/concepts/catalog/

Maintainer: vnvspec core team
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement


def hello_world() -> list[Requirement]:
    """Trivial catalog example. Used by tests to validate the catalog convention."""
    return [
        Requirement(
            id="CAT-DEMO-001",
            statement="The system shall produce deterministic output for the test input 'hello'.",
            rationale="Smoke-test requirement to validate catalog import surface.",
            verification_method="test",
            acceptance_criteria=["greet('hello') == 'hello, world'"],
            source="https://ai-vnv.github.io/vnvspec/catalog/demo/",  # type: ignore[arg-type]
        ),
    ]
