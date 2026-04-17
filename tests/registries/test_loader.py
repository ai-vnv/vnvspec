"""Tests for the standards registry loader."""

from __future__ import annotations

import pytest

from vnvspec.registries.loader import (
    Registry,
    RegistryEntry,
    RegistryError,
    list_available,
    list_clauses,
    load,
)

EXPECTED_REGISTRIES = [
    "eu_ai_act",
    "iso_21448",
    "iso_pas_8800",
    "nist_ai_rmf",
    "ul_4600",
]

MIN_ENTRIES = 30


class TestListAvailable:
    def test_returns_all_five(self) -> None:
        names = list_available()
        for expected in EXPECTED_REGISTRIES:
            assert expected in names, f"Missing registry: {expected}"

    def test_sorted(self) -> None:
        names = list_available()
        assert names == sorted(names)


class TestLoad:
    @pytest.mark.parametrize("name", EXPECTED_REGISTRIES)
    def test_load_each_registry(self, name: str) -> None:
        registry = load(name)
        assert isinstance(registry, Registry)
        assert len(registry.entries) >= MIN_ENTRIES, (
            f"{name} has only {len(registry.entries)} entries, need >= {MIN_ENTRIES}"
        )

    @pytest.mark.parametrize("name", EXPECTED_REGISTRIES)
    def test_entries_have_required_fields(self, name: str) -> None:
        registry = load(name)
        for entry in registry.entries:
            assert entry.id, f"Empty id in {name}"
            assert entry.clause, f"Empty clause in {name}"
            assert entry.title, f"Empty title in {name}"

    @pytest.mark.parametrize("name", EXPECTED_REGISTRIES)
    def test_unique_ids(self, name: str) -> None:
        registry = load(name)
        ids = [e.id for e in registry.entries]
        assert len(ids) == len(set(ids)), f"Duplicate IDs in {name}"

    @pytest.mark.parametrize("name", EXPECTED_REGISTRIES)
    def test_has_disclaimer(self, name: str) -> None:
        registry = load(name)
        assert "not a substitute" in registry.disclaimer.lower()

    def test_load_nonexistent_raises(self) -> None:
        with pytest.raises(RegistryError, match="not found"):
            load("nonexistent_standard")

    def test_error_lists_available(self) -> None:
        with pytest.raises(RegistryError, match="iso_pas_8800"):
            load("nonexistent_standard")


class TestListClauses:
    def test_iso_pas_8800_clauses(self) -> None:
        clauses = list_clauses("iso_pas_8800")
        assert len(clauses) >= MIN_ENTRIES


class TestRegistryModel:
    def test_construction(self) -> None:
        entry = RegistryEntry(
            id="test-1",
            clause="1.1",
            title="Test",
            summary="A test entry.",
            normative_level="shall",
        )
        registry = Registry(name="Test", entries=[entry])
        assert registry.name == "Test"
        assert len(registry.entries) == 1

    def test_json_round_trip(self) -> None:
        registry = load("iso_pas_8800")
        data = registry.model_dump()
        registry2 = Registry.model_validate(data)
        assert len(registry2.entries) == len(registry.entries)
