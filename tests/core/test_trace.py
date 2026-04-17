"""Tests for the traceability graph."""

from __future__ import annotations

import json

import pytest

from vnvspec.core.errors import SpecError
from vnvspec.core.trace import (
    TraceLink,
    build_trace_graph,
    coverage_report,
    export_graphml,
    import_graphml,
)


class TestTraceLink:
    def test_construction(self) -> None:
        link = TraceLink(source_id="REQ-001", target_id="HAZ-001", relation="mitigates")
        assert link.source_id == "REQ-001"
        assert link.target_id == "HAZ-001"
        assert link.relation == "mitigates"

    def test_with_metadata(self) -> None:
        link = TraceLink(
            source_id="EV-001",
            target_id="REQ-001",
            relation="verifies",
            metadata={"confidence": "high"},
        )
        assert link.metadata["confidence"] == "high"


class TestBuildTraceGraph:
    def test_basic_graph(self) -> None:
        links = [
            TraceLink(source_id="REQ-001", target_id="HAZ-001", relation="mitigates"),
            TraceLink(source_id="EV-001", target_id="REQ-001", relation="verifies"),
        ]
        graph = build_trace_graph(links)
        assert len(graph.edges) == 2
        assert len(graph.nodes) == 3

    def test_empty_links(self) -> None:
        graph = build_trace_graph([])
        assert len(graph.edges) == 0

    def test_cycle_detection(self) -> None:
        links = [
            TraceLink(source_id="A", target_id="B", relation="derives_from"),
            TraceLink(source_id="B", target_id="C", relation="derives_from"),
            TraceLink(source_id="C", target_id="A", relation="derives_from"),
        ]
        with pytest.raises(SpecError, match="cycle"):
            build_trace_graph(links)

    def test_edge_attributes(self) -> None:
        link = TraceLink(
            source_id="EV-001",
            target_id="REQ-001",
            relation="verifies",
            metadata={"tool": "pytest"},
        )
        graph = build_trace_graph([link])
        edge_data = graph.edges["EV-001", "REQ-001"]
        assert edge_data["relation"] == "verifies"
        assert json.loads(edge_data["metadata_json"])["tool"] == "pytest"

    def test_acyclic_diamond(self) -> None:
        links = [
            TraceLink(source_id="A", target_id="B", relation="derives_from"),
            TraceLink(source_id="A", target_id="C", relation="derives_from"),
            TraceLink(source_id="B", target_id="D", relation="derives_from"),
            TraceLink(source_id="C", target_id="D", relation="derives_from"),
        ]
        graph = build_trace_graph(links)
        assert len(graph.edges) == 4


class TestCoverageReport:
    def test_basic_coverage(self) -> None:
        links = [
            TraceLink(source_id="EV-001", target_id="REQ-001", relation="verifies"),
            TraceLink(source_id="REQ-001", target_id="HAZ-001", relation="mitigates"),
        ]
        graph = build_trace_graph(links)
        report = coverage_report(graph, ["REQ-001"])
        assert "REQ-001" in report
        assert "verifies" in report["REQ-001"]
        assert "EV-001" in report["REQ-001"]["verifies"]
        assert "mitigates" in report["REQ-001"]
        assert "HAZ-001" in report["REQ-001"]["mitigates"]

    def test_uncovered_requirement(self) -> None:
        graph = build_trace_graph([])
        report = coverage_report(graph, ["REQ-999"])
        assert report["REQ-999"] == {}

    def test_multiple_requirements(self) -> None:
        links = [
            TraceLink(source_id="EV-001", target_id="REQ-001", relation="verifies"),
            TraceLink(source_id="EV-002", target_id="REQ-002", relation="verifies"),
        ]
        graph = build_trace_graph(links)
        report = coverage_report(graph, ["REQ-001", "REQ-002"])
        assert len(report) == 2
        assert "EV-001" in report["REQ-001"]["verifies"]
        assert "EV-002" in report["REQ-002"]["verifies"]


class TestGraphMLRoundTrip:
    def test_export_import(self) -> None:
        links = [
            TraceLink(source_id="A", target_id="B", relation="derives_from"),
            TraceLink(source_id="B", target_id="C", relation="refines"),
        ]
        graph = build_trace_graph(links)
        xml = export_graphml(graph)
        assert "graphml" in xml

        graph2 = import_graphml(xml)
        assert len(graph2.edges) == 2
        assert len(graph2.nodes) == 3

    def test_export_contains_attributes(self) -> None:
        link = TraceLink(source_id="X", target_id="Y", relation="satisfies")
        graph = build_trace_graph([link])
        xml = export_graphml(graph)
        assert "satisfies" in xml
