"""Traceability graph — links between requirements, hazards, evidence, and ODDs.

Builds a directed acyclic graph (DAG) using networkx to represent
traceability relationships.

Example:
    >>> link = TraceLink(source_id="REQ-001", target_id="HAZ-001", relation="mitigates")
    >>> link.relation
    'mitigates'
"""

from __future__ import annotations

import json as _json
from io import BytesIO
from typing import Any, Literal

import networkx as nx
from pydantic import BaseModel, Field

from vnvspec.core.errors import SpecError

Relation = Literal[
    "derives_from",
    "refines",
    "mitigates",
    "verifies",
    "satisfies",
    "references_ontology",
    "maps_to_standard",
]


class TraceLink(BaseModel):
    """A directed link between two entities in the traceability graph.

    Example:
        >>> link = TraceLink(
        ...     source_id="EV-001", target_id="REQ-001", relation="verifies",
        ... )
        >>> link.source_id
        'EV-001'
    """

    model_config = {"frozen": True}

    source_id: str = Field(description="ID of the source entity.")
    target_id: str = Field(description="ID of the target entity.")
    relation: Relation = Field(description="Type of traceability relationship.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional link metadata.")


def build_trace_graph(links: list[TraceLink]) -> nx.DiGraph:
    """Build a directed graph from a list of trace links.

    Raises :class:`SpecError` if the resulting graph contains a cycle.

    Example:
        >>> link = TraceLink(source_id="REQ-001", target_id="HAZ-001", relation="mitigates")
        >>> g = build_trace_graph([link])
        >>> len(g.edges)
        1
    """
    graph: nx.DiGraph = nx.DiGraph()
    for link in links:
        graph.add_edge(
            link.source_id,
            link.target_id,
            relation=link.relation,
            metadata_json=_json.dumps(link.metadata) if link.metadata else "",
        )

    if not nx.is_directed_acyclic_graph(graph):  # type: ignore[no-untyped-call]  # networkx stubs incomplete
        cycles = list(nx.simple_cycles(graph))
        raise SpecError(
            f"Traceability graph contains cycle(s): {cycles}. "
            "Links must form a directed acyclic graph."
        )

    return graph


def coverage_report(
    graph: nx.DiGraph,
    requirement_ids: list[str],
) -> dict[str, dict[str, list[str]]]:
    """Generate a coverage report showing which entities are linked to each requirement.

    For each requirement, returns the list of nodes connected via incoming
    edges (e.g., evidence that verifies it) and outgoing edges (e.g., hazards
    it mitigates), grouped by relation type.

    Example:
        >>> link = TraceLink(source_id="EV-001", target_id="REQ-001", relation="verifies")
        >>> g = build_trace_graph([link])
        >>> report = coverage_report(g, ["REQ-001"])
        >>> "REQ-001" in report
        True
    """
    result: dict[str, dict[str, list[str]]] = {}

    for req_id in requirement_ids:
        linked: dict[str, list[str]] = {}

        if req_id in graph:
            for pred in graph.predecessors(req_id):  # type: ignore[no-untyped-call]  # networkx stubs
                edge_data = graph.edges[pred, req_id]
                relation: str = edge_data["relation"]
                linked.setdefault(relation, []).append(pred)

            for succ in graph.successors(req_id):  # type: ignore[no-untyped-call]  # networkx stubs
                edge_data = graph.edges[req_id, succ]
                relation = edge_data["relation"]
                linked.setdefault(relation, []).append(succ)

        result[req_id] = linked

    return result


def export_graphml(graph: nx.DiGraph) -> str:
    """Export the trace graph as a GraphML string.

    Example:
        >>> link = TraceLink(source_id="A", target_id="B", relation="derives_from")
        >>> g = build_trace_graph([link])
        >>> xml = export_graphml(g)
        >>> "graphml" in xml
        True
    """
    buf = BytesIO()
    nx.write_graphml(graph, buf)
    return buf.getvalue().decode("utf-8")


def import_graphml(graphml_str: str) -> nx.DiGraph:
    """Import a trace graph from a GraphML string.

    Example:
        >>> link = TraceLink(source_id="A", target_id="B", relation="derives_from")
        >>> g = build_trace_graph([link])
        >>> xml = export_graphml(g)
        >>> g2 = import_graphml(xml)
        >>> len(g2.edges)
        1
    """
    buf = BytesIO(graphml_str.encode("utf-8"))
    return nx.read_graphml(buf)  # type: ignore[no-any-return]  # networkx stubs incomplete
