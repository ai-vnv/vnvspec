"""EU AI Act Annex IV technical documentation exporter."""

from __future__ import annotations

from vnvspec.core.assessment import Report


def export_annex_iv(report: Report) -> str:
    """Export *report* as an EU AI Act Annex IV structured document.

    Returns a Markdown-formatted document with Annex IV headings populated
    from the report data.

    Example:
        >>> from vnvspec.core.assessment import Report
        >>> doc = export_annex_iv(Report(spec_name="demo", spec_version="1.0"))
        >>> "Annex IV" in doc
        True
    """
    sections: list[str] = [
        "# EU AI Act — Annex IV Technical Documentation",
        "",
        f"**System**: {report.spec_name} v{report.spec_version}",
        f"**Date**: {report.created_at.isoformat()}",
        "",
        "---",
        "",
        "## 1. Intended Purpose",
        "",
        f"System name: {report.spec_name}",
        f"Version: {report.spec_version}",
        f"Overall verdict: {report.verdict()}",
        "",
        "## 2. Design and Development",
        "",
        f"Total evidence items: {len(report.evidence)}",
        f"Pass: {report.pass_count()} | Fail: {report.fail_count()}",
        "",
    ]

    # Group by kind
    kinds: dict[str, list[str]] = {}
    for ev in report.evidence:
        kinds.setdefault(ev.kind, []).append(ev.id)
    if kinds:
        sections.append("Verification activities by kind:")
        sections.append("")
        for kind, ids in sorted(kinds.items()):
            sections.append(f"- **{kind}**: {', '.join(sorted(ids))}")
        sections.append("")

    sections.extend(
        [
            "## 3. Performance Metrics",
            "",
        ]
    )

    if report.summary:
        for key, val in sorted(report.summary.items()):
            sections.append(f"- {key}: {val}")
        sections.append("")
    else:
        sections.append("_No summary metrics provided._")
        sections.append("")

    sections.extend(
        [
            "## 4. Risk Management and V&V Evidence",
            "",
            "| ID | Requirement | Kind | Verdict | Observed |",
            "|---|---|---|---|---|",
        ]
    )

    for ev in sorted(report.evidence, key=lambda e: e.requirement_id):
        sections.append(
            f"| {ev.id} | {ev.requirement_id} | {ev.kind} "
            f"| {ev.verdict} | {ev.observed_at.isoformat()} |"
        )

    sections.extend(
        [
            "",
            "## 5. Monitoring, Functioning, and Control",
            "",
            f"Metadata: {report.metadata if report.metadata else '_none_'}",
            "",
            "---",
            f"_Generated from vnvspec report for {report.spec_name}._",
            "",
        ]
    )

    return "\n".join(sections)
