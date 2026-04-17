"""HTML exporter — standalone HTML with embedded CSS."""

from __future__ import annotations

from pathlib import Path

from vnvspec.core.assessment import Report

_CSS = """\
body { font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; }
h1 { border-bottom: 2px solid #0066cc; padding-bottom: .5rem; }
h2 { color: #0066cc; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #ccc; padding: .5rem .75rem; text-align: left; }
th { background: #f0f4f8; }
.pass { color: #16a34a; font-weight: bold; }
.fail { color: #dc2626; font-weight: bold; }
.inconclusive { color: #d97706; font-weight: bold; }
.summary { background: #f8fafc; padding: 1rem; border-radius: .5rem; margin: 1rem 0; }
"""


def _verdict_span(verdict: str) -> str:
    return f'<span class="{verdict}">{verdict}</span>'


def export_html(report: Report, path: Path | None = None) -> str:
    """Export *report* as a standalone HTML document.

    If *path* is given the HTML is also written to that file.

    Example:
        >>> from vnvspec.core.assessment import Report
        >>> html = export_html(Report(spec_name="demo", spec_version="1.0"))
        >>> "<html>" in html and "</html>" in html
        True
    """
    sorted_evidence = sorted(report.evidence, key=lambda e: e.requirement_id)

    rows: list[str] = []
    for ev in sorted_evidence:
        rows.append(
            "<tr>"
            f"<td>{ev.id}</td>"
            f"<td>{ev.requirement_id}</td>"
            f"<td>{ev.kind}</td>"
            f"<td>{_verdict_span(ev.verdict)}</td>"
            f"<td>{ev.artifact_uri}</td>"
            f"<td>{ev.observed_at.isoformat()}</td>"
            "</tr>"
        )

    evidence_table = (
        "<table>\n"
        "<tr><th>ID</th><th>Requirement</th><th>Kind</th>"
        "<th>Verdict</th><th>Artifact</th><th>Observed</th></tr>\n" + "\n".join(rows) + "\n</table>"
    )

    html = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        f"<title>V&amp;V Report — {report.spec_name}</title>\n"
        f"<style>\n{_CSS}</style>\n"
        "</head>\n<body>\n"
        f"<h1>V&amp;V Report: {report.spec_name} v{report.spec_version}</h1>\n"
        f"<p>Created: {report.created_at.isoformat()}</p>\n"
        '<div class="summary">\n'
        f"<h2>Summary</h2>\n"
        f"<p>Overall verdict: {_verdict_span(report.verdict())}</p>\n"
        f"<p>Pass: {report.pass_count()} | Fail: {report.fail_count()} "
        f"| Inconclusive: {report.inconclusive_count()} "
        f"| Total: {len(report.evidence)}</p>\n"
        "</div>\n"
        f"<h2>Evidence</h2>\n{evidence_table}\n"
        "</body>\n</html>\n"
    )

    if path is not None:
        path.write_text(html, encoding="utf-8")

    return html
