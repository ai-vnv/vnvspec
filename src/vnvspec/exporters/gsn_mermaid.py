"""GSN assurance case exported as a Mermaid flowchart."""

from __future__ import annotations

from vnvspec.core.assessment import Report


def _sanitize(text: str) -> str:
    """Escape characters that break Mermaid labels."""
    return text.replace('"', "'").replace("\n", " ")


def export_gsn_mermaid(report: Report) -> str:
    """Export *report* as a GSN-style Mermaid flowchart.

    The chart has:
    * A top-level claim node (overall verdict).
    * Sub-claim nodes per unique requirement.
    * Evidence (solution) leaf nodes.

    Example:
        >>> from vnvspec.core.assessment import Report
        >>> mmd = export_gsn_mermaid(Report(spec_name="demo"))
        >>> mmd.startswith("flowchart TD")
        True
    """
    lines: list[str] = ["flowchart TD"]

    top_id = "G1"
    top_label = _sanitize(f"{report.spec_name} v{report.spec_version}: {report.verdict()}")
    lines.append(f'    {top_id}["{top_label}"]')

    # Group evidence by requirement
    req_ids: dict[str, list[str]] = {}
    for ev in report.evidence:
        req_ids.setdefault(ev.requirement_id, []).append(ev.id)

    for idx, (req_id, ev_ids) in enumerate(sorted(req_ids.items()), start=1):
        sub_node = f"S{idx}"
        lines.append(f'    {sub_node}["{_sanitize(req_id)}"]')
        lines.append(f"    {top_id} --> {sub_node}")

        for ev_id in sorted(ev_ids):
            ev_obj = next(e for e in report.evidence if e.id == ev_id)
            leaf = f"E_{ev_id}".replace("-", "_")
            leaf_label = _sanitize(f"{ev_id}: {ev_obj.verdict}")
            lines.append(f'    {leaf}["{leaf_label}"]')
            lines.append(f"    {sub_node} --> {leaf}")

    lines.append("")
    return "\n".join(lines)
