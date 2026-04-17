"""Shared visualization helpers for vnvspec tutorial notebooks.

Provides styled HTML tables, matplotlib charts, and display utilities
for requirements, evidence, reports, and traceability graphs.
"""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# HTML / IPython display helpers
# ---------------------------------------------------------------------------

_TABLE_CSS = """
<style>
.vnv-table { border-collapse: collapse; width: 100%; font-family: system-ui, sans-serif; font-size: 14px; margin: 12px 0; }
.vnv-table th { background: #1a1a2e; color: #fff; padding: 10px 14px; text-align: left; font-weight: 600; }
.vnv-table td { padding: 8px 14px; border-bottom: 1px solid #e0e0e0; }
.vnv-table tr:nth-child(even) { background: #f8f9fa; }
.vnv-table tr:hover { background: #e8f0fe; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.badge-pass { background: #d4edda; color: #155724; }
.badge-fail { background: #f8d7da; color: #721c24; }
.badge-inconclusive { background: #fff3cd; color: #856404; }
.badge-error { background: #f8d7da; color: #721c24; }
.badge-warning { background: #fff3cd; color: #856404; }
.card { border: 1px solid #dee2e6; border-radius: 8px; padding: 16px; margin: 8px 0; background: #fff; }
.card-title { font-weight: 700; font-size: 16px; margin-bottom: 8px; }
.card-field { color: #555; font-size: 13px; margin: 4px 0; }
</style>
"""


def _badge(text: str) -> str:
    cls = f"badge-{text}" if text in ("pass", "fail", "inconclusive", "error", "warning") else "badge"
    return f'<span class="badge {cls}">{text}</span>'


def display_requirements_table(requirements: list[Any]) -> str:
    """Render a list of Requirement objects as a styled HTML table.

    Returns the HTML string and displays it in Jupyter.
    """
    from IPython.display import HTML, display  # noqa: PLC0415

    rows = []
    for r in requirements:
        rows.append(
            f"<tr><td><b>{r.id}</b></td>"
            f"<td>{r.statement}</td>"
            f"<td>{r.verification_method}</td>"
            f"<td>{r.priority}</td></tr>"
        )
    html = (
        _TABLE_CSS
        + '<table class="vnv-table">'
        + "<tr><th>ID</th><th>Statement</th><th>Method</th><th>Priority</th></tr>"
        + "".join(rows)
        + "</table>"
    )
    display(HTML(html))
    return html


def display_violations_table(violations: list[Any]) -> str:
    """Render GtWR RuleViolation objects as a styled HTML table."""
    from IPython.display import HTML, display  # noqa: PLC0415

    if not violations:
        html = _TABLE_CSS + '<div class="card"><b>No violations found.</b> All quality checks passed.</div>'
        display(HTML(html))
        return html

    rows = []
    for v in violations:
        rows.append(
            f"<tr><td><b>{v.rule}</b></td>"
            f"<td>{v.name}</td>"
            f"<td>{_badge(v.severity)}</td>"
            f"<td>{v.message}</td></tr>"
        )
    html = (
        _TABLE_CSS
        + '<table class="vnv-table">'
        + "<tr><th>Rule</th><th>Name</th><th>Severity</th><th>Message</th></tr>"
        + "".join(rows)
        + "</table>"
    )
    display(HTML(html))
    return html


def display_evidence_table(evidence_list: list[Any]) -> str:
    """Render Evidence objects as a styled HTML table."""
    from IPython.display import HTML, display  # noqa: PLC0415

    rows = []
    for e in evidence_list:
        rows.append(
            f"<tr><td><b>{e.id}</b></td>"
            f"<td>{e.requirement_id}</td>"
            f"<td>{e.kind}</td>"
            f"<td>{_badge(e.verdict)}</td>"
            f"<td>{e.observed_at.strftime('%Y-%m-%d %H:%M')}</td></tr>"
        )
    html = (
        _TABLE_CSS
        + '<table class="vnv-table">'
        + "<tr><th>Evidence ID</th><th>Requirement</th><th>Kind</th><th>Verdict</th><th>Observed</th></tr>"
        + "".join(rows)
        + "</table>"
    )
    display(HTML(html))
    return html


def display_report_summary(report: Any) -> str:
    """Display a styled summary card for a Report."""
    from IPython.display import HTML, display  # noqa: PLC0415

    verdict = report.verdict()
    html = (
        _TABLE_CSS
        + f'<div class="card">'
        + f'<div class="card-title">Assessment Report: {report.spec_name} v{report.spec_version}</div>'
        + f'<div class="card-field">Overall Verdict: {_badge(verdict)}</div>'
        + f'<div class="card-field">Evidence items: {len(report.evidence)}</div>'
        + f'<div class="card-field">Pass: {report.pass_count()} | Fail: {report.fail_count()}</div>'
        + f'<div class="card-field">Created: {report.created_at.strftime("%Y-%m-%d %H:%M UTC")}</div>'
        + "</div>"
    )
    display(HTML(html))
    return html


def display_requirement_card(req: Any) -> str:
    """Display a styled card for a single Requirement."""
    from IPython.display import HTML, display  # noqa: PLC0415

    criteria_html = "".join(f"<li>{c}</li>" for c in req.acceptance_criteria)
    html = (
        _TABLE_CSS
        + f'<div class="card">'
        + f'<div class="card-title">{req.id}: {req.statement}</div>'
        + f'<div class="card-field"><b>Rationale:</b> {req.rationale}</div>'
        + f'<div class="card-field"><b>Method:</b> {req.verification_method} | <b>Priority:</b> {req.priority}</div>'
        + (f'<div class="card-field"><b>Acceptance criteria:</b><ul>{criteria_html}</ul></div>' if criteria_html else "")
        + "</div>"
    )
    display(HTML(html))
    return html


# ---------------------------------------------------------------------------
# Matplotlib chart helpers
# ---------------------------------------------------------------------------

def plot_violations_by_rule(violations: list[Any], title: str = "Violations by Rule") -> None:
    """Bar chart of violation counts grouped by rule."""
    import matplotlib.pyplot as plt  # noqa: PLC0415

    if not violations:
        print("No violations to plot.")
        return

    counts: dict[str, int] = {}
    for v in violations:
        label = f"{v.rule} ({v.name})"
        counts[label] = counts.get(label, 0) + 1

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#dc3545" if "error" in str(v.severity) else "#ffc107" for v in violations]
    # Deduplicate colors to match counts
    color_map: dict[str, str] = {}
    for v in violations:
        label = f"{v.rule} ({v.name})"
        color_map[label] = "#dc3545" if v.severity == "error" else "#ffc107"

    bars = ax.barh(list(counts.keys()), list(counts.values()),
                   color=[color_map[k] for k in counts])
    ax.set_xlabel("Count")
    ax.set_title(title)
    ax.invert_yaxis()
    for bar, count in zip(bars, counts.values()):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                str(count), va="center", fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_evidence_verdicts(evidence_list: list[Any], title: str = "Evidence Verdicts") -> None:
    """Pie chart of evidence verdicts."""
    import matplotlib.pyplot as plt  # noqa: PLC0415

    if not evidence_list:
        print("No evidence to plot.")
        return

    counts: dict[str, int] = {}
    for e in evidence_list:
        counts[e.verdict] = counts.get(e.verdict, 0) + 1

    color_map = {"pass": "#28a745", "fail": "#dc3545", "inconclusive": "#ffc107"}
    labels = list(counts.keys())
    sizes = list(counts.values())
    colors = [color_map.get(l, "#6c757d") for l in labels]

    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, colors=colors, autopct="%1.0f%%",
        startangle=90, textprops={"fontsize": 13}
    )
    for t in autotexts:
        t.set_fontweight("bold")
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_coverage(spec: Any, title: str = "Requirement Coverage") -> None:
    """Bar chart showing covered vs uncovered requirements."""
    import matplotlib.pyplot as plt  # noqa: PLC0415

    summary = spec.coverage_summary()
    labels = ["Covered", "Uncovered"]
    values = [summary["covered"], summary["uncovered"]]
    colors = ["#28a745", "#dc3545"]

    fig, ax = plt.subplots(figsize=(5, 3))
    bars = ax.bar(labels, values, color=colors, width=0.5)
    ax.set_ylabel("Requirements")
    ax.set_title(title, fontweight="bold")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                str(val), ha="center", fontweight="bold")
    plt.tight_layout()
    plt.show()


def plot_trace_graph(links: list[Any]) -> None:
    """Visualize a traceability graph using networkx + matplotlib."""
    import matplotlib.pyplot as plt  # noqa: PLC0415
    import networkx as nx  # noqa: PLC0415
    from vnvspec.core.trace import build_trace_graph  # noqa: PLC0415

    graph = build_trace_graph(links)

    color_map = []
    for node in graph.nodes():
        if str(node).startswith("REQ"):
            color_map.append("#4dabf7")
        elif str(node).startswith("EV"):
            color_map.append("#69db7c")
        elif str(node).startswith("HAZ"):
            color_map.append("#ff6b6b")
        else:
            color_map.append("#dee2e6")

    fig, ax = plt.subplots(figsize=(10, 6))
    pos = nx.spring_layout(graph, seed=42, k=2)
    nx.draw(graph, pos, ax=ax, with_labels=True, node_color=color_map,
            node_size=2000, font_size=9, font_weight="bold",
            edge_color="#adb5bd", arrows=True, arrowsize=20)

    edge_labels = nx.get_edge_attributes(graph, "relation")
    nx.draw_networkx_edge_labels(graph, pos, edge_labels, font_size=8, font_color="#495057")
    ax.set_title("Traceability Graph", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.show()


def display_registry_sample(name: str, n: int = 10) -> str:
    """Display the first n entries of a standards registry."""
    from IPython.display import HTML, display  # noqa: PLC0415
    from vnvspec.registries import load  # noqa: PLC0415

    registry = load(name)
    rows = []
    for entry in registry.entries[:n]:
        rows.append(
            f"<tr><td><b>{entry.clause}</b></td>"
            f"<td>{entry.title}</td>"
            f"<td>{_badge(entry.normative_level) if entry.normative_level in ('shall', 'should', 'may') else entry.normative_level}</td>"
            f"<td>{entry.summary[:80]}{'...' if len(entry.summary) > 80 else ''}</td></tr>"
        )
    html = (
        _TABLE_CSS
        + f'<h4>{registry.name} ({len(registry.entries)} clauses)</h4>'
        + '<table class="vnv-table">'
        + "<tr><th>Clause</th><th>Title</th><th>Level</th><th>Summary</th></tr>"
        + "".join(rows)
        + "</table>"
        + f'<p style="color:#888; font-size:12px;">{registry.disclaimer}</p>'
    )
    display(HTML(html))
    return html


def display_mermaid(mermaid_code: str) -> None:
    """Render a Mermaid diagram in Jupyter (requires mermaid JS or falls back to code)."""
    from IPython.display import HTML, display  # noqa: PLC0415

    html = f"""
    <div class="mermaid">{mermaid_code}</div>
    <script type="module">
      import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
      mermaid.initialize({{ startOnLoad: true }});
    </script>
    """
    display(HTML(html))
