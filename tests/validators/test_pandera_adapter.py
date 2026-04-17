"""Tests for the pandera validator adapter."""

from __future__ import annotations

import pandas as pd
import pandera as pa

from vnvspec.validators.pandera_adapter import pandera_schema, validate_dataframe


class TestPanderaSchema:
    def test_extracts_invariants(self) -> None:
        schema = pa.DataFrameSchema(
            {
                "x": pa.Column(int),
                "y": pa.Column(float),
            }
        )
        invariants = pandera_schema(schema)
        names = {i.name for i in invariants}
        assert "x" in names
        assert "y" in names

    def test_invariant_count(self) -> None:
        schema = pa.DataFrameSchema(
            {
                "a": pa.Column(int),
                "b": pa.Column(float),
                "c": pa.Column(str),
            }
        )
        invariants = pandera_schema(schema)
        assert len(invariants) == 3


class TestValidateDataFrame:
    def test_valid_dataframe_passes(self) -> None:
        schema = pa.DataFrameSchema({"score": pa.Column(float, pa.Check.in_range(0, 1))})
        df = pd.DataFrame({"score": [0.1, 0.5, 0.9]})
        ev = validate_dataframe(schema, df)
        assert ev.verdict == "pass"
        assert ev.details["validator"] == "pandera"
        assert ev.details["rows"] == 3

    def test_invalid_dataframe_fails(self) -> None:
        schema = pa.DataFrameSchema({"score": pa.Column(float, pa.Check.in_range(0, 1))})
        df = pd.DataFrame({"score": [0.1, 2.0, 0.9]})
        ev = validate_dataframe(schema, df)
        assert ev.verdict == "fail"
        assert "errors" in ev.details

    def test_missing_column_fails(self) -> None:
        schema = pa.DataFrameSchema({"score": pa.Column(float)})
        df = pd.DataFrame({"other": [1.0, 2.0]})
        ev = validate_dataframe(schema, df)
        assert ev.verdict == "fail"

    def test_requirement_id_propagated(self) -> None:
        schema = pa.DataFrameSchema({"x": pa.Column(int)})
        df = pd.DataFrame({"x": [1, 2, 3]})
        ev = validate_dataframe(schema, df, requirement_id="REQ-002")
        assert ev.requirement_id == "REQ-002"
