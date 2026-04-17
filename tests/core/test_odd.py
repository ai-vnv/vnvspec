"""Tests for the ODD model."""

from __future__ import annotations

import json

from vnvspec.core.odd import ODD


class TestODD:
    def test_construction(self) -> None:
        odd = ODD(
            name="highway",
            dimensions={"speed_range_kmh": [60, 120], "weather": ["clear", "rain"]},
        )
        assert odd.name == "highway"
        assert "speed_range_kmh" in odd.dimensions

    def test_minimal(self) -> None:
        odd = ODD(name="empty")
        assert odd.dimensions == {}
        assert odd.source_ontology is None

    def test_with_ontology(self) -> None:
        odd = ODD(name="urban", dimensions={"speed": [0, 50]}, source_ontology="bsi_pas_1883")
        assert odd.source_ontology == "bsi_pas_1883"

    def test_dimension_names(self) -> None:
        odd = ODD(name="test", dimensions={"c": [1], "a": [2], "b": [3]})
        assert odd.dimension_names() == ["a", "b", "c"]

    def test_dimension_names_empty(self) -> None:
        odd = ODD(name="test")
        assert odd.dimension_names() == []

    def test_json_round_trip(self) -> None:
        odd = ODD(
            name="test",
            dimensions={"speed": [0, 100]},
            source_ontology="test_ontology",
            metadata={"version": 1},
        )
        data = json.loads(odd.model_dump_json())
        odd2 = ODD.model_validate(data)
        assert odd.name == odd2.name
        assert odd.dimensions == odd2.dimensions
