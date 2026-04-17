"""Markdown exporter."""

from __future__ import annotations

from pathlib import Path

from vnvspec.core.assessment import Report


def export_markdown(report: Report, path: Path | None = None) -> str:
    """Export *report* as a Markdown document.

    If *path* is given the Markdown is also written to that file.

    Example:
        >>> from vnvspec.core.assessment import Report
        >>> md = export_markdown(Report(spec_name="demo", spec_version="1.0"))
        >>> "# V&V Report" in md
        True
    """
    lines: list[str] = [
        f"# V&V Report: {report.spec_name} v{report.spec_version}",
        "",
        f"Created: {report.created_at.isoformat()}",
        "",
        "## Summary",
        "",
        f"- **Overall verdict**: {report.verdict()}",
        f"- **Pass**: {report.pass_count()}",
        f"- **Fail**: {report.fail_count()}",
        f"- **Total evidence**: {len(report.evidence)}",
        "",
        "## Evidence",
        "",
        "| ID | Requirement | Kind | Verdict | Artifact | Observed |",
        "|---|---|---|---|---|---|",
    ]

    sorted_evidence = sorted(report.evidence, key=lambda e: e.requirement_id)
    for ev in sorted_evidence:
        lines.append(
            f"| {ev.id} | {ev.requirement_id} | {ev.kind} "
            f"| **{ev.verdict}** | {ev.artifact_uri} | {ev.observed_at.isoformat()} |"
        )

    lines.append("")
    md = "\n".join(lines)

    if path is not None:
        path.write_text(md, encoding="utf-8")

    return md
