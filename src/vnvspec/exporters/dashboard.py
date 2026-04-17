"""Dashboard exporter — generates a static V&V dashboard site.

Produces a multi-page HTML site with:
- Summary page with standards compliance, evidence overview, badge
- Per-requirement detail pages with evidence, version history, acceptance criteria
- Locally generated badge SVG with optional link to hosted dashboard

The site can be deployed to GitHub Pages alongside project docs.
"""

from __future__ import annotations

import html as html_lib
from pathlib import Path
from typing import Any

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.exporters.badge import export_badge

_CSS = """\
:root {
  --bg: #ffffff; --fg: #1a1a2e; --accent: #0f3460; --accent2: #16213e;
  --pass: #16a34a; --fail: #dc2626; --inconclusive: #d97706; --info: #6366f1;
  --border: #e2e8f0; --bg2: #f8fafc; --bg3: #f1f5f9;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a; --fg: #e2e8f0; --accent: #60a5fa; --accent2: #93c5fd;
    --border: #334155; --bg2: #1e293b; --bg3: #1e293b;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', system-ui, -apple-system, sans-serif; background: var(--bg);
  color: var(--fg); line-height: 1.6; }
.container { max-width: 1100px; margin: 0 auto; padding: 2rem; }
header { background: var(--accent2); color: #fff; padding: 2rem 0; margin-bottom: 2rem; }
header .container { display: flex; align-items: center; gap: 1.5rem; }
header h1 { font-size: 1.5rem; font-weight: 600; }
header .badge { flex-shrink: 0; }
nav { background: var(--bg2); border-bottom: 1px solid var(--border); padding: 0.5rem 0; }
nav .container { display: flex; gap: 1rem; flex-wrap: wrap; }
nav a { color: var(--accent); text-decoration: none; padding: 0.25rem 0.75rem;
  border-radius: 4px; font-size: 0.875rem; }
nav a:hover { background: var(--bg3); }
nav a.active { background: var(--accent); color: #fff; }
h2 { color: var(--accent); margin: 1.5rem 0 0.75rem; font-size: 1.25rem;
  border-bottom: 2px solid var(--border); padding-bottom: 0.5rem; }
h3 { color: var(--accent); margin: 1rem 0 0.5rem; font-size: 1.1rem; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: 0.9rem; }
th, td { border: 1px solid var(--border); padding: 0.5rem 0.75rem; text-align: left; }
th { background: var(--bg2); font-weight: 600; }
tr:hover { background: var(--bg3); }
.pass { color: var(--pass); font-weight: 700; }
.fail { color: var(--fail); font-weight: 700; }
.inconclusive { color: var(--inconclusive); font-weight: 700; }
.card { background: var(--bg2); border: 1px solid var(--border); border-radius: 8px;
  padding: 1.25rem; margin: 0.75rem 0; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem; margin: 1rem 0; }
.stat { text-align: center; padding: 1rem; background: var(--bg2); border-radius: 8px;
  border: 1px solid var(--border); }
.stat .number { font-size: 2rem; font-weight: 700; }
.stat .label { font-size: 0.8rem; color: var(--fg); opacity: 0.7; text-transform: uppercase; }
.tag { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 3px;
  font-size: 0.75rem; font-weight: 600; }
.tag-pass { background: #dcfce7; color: #166534; }
.tag-fail { background: #fee2e2; color: #991b1b; }
.tag-inconclusive { background: #fef3c7; color: #92400e; }
.tag-version { background: #e0e7ff; color: #3730a3; }
.tag-blocking { background: #fee2e2; color: #991b1b; }
.tag-high { background: #fef3c7; color: #92400e; }
.tag-medium { background: #e0e7ff; color: #3730a3; }
.tag-low { background: #f1f5f9; color: #475569; }
.timeline { border-left: 3px solid var(--border); padding-left: 1rem; margin: 1rem 0; }
.timeline-entry { margin-bottom: 0.75rem; padding: 0.5rem; }
a { color: var(--accent); }
.footer { margin-top: 3rem; padding: 1rem 0; border-top: 1px solid var(--border);
  font-size: 0.8rem; opacity: 0.6; text-align: center; }
"""


def export_dashboard(
    spec: Spec,
    report: Report,
    *,
    output_dir: Path | str,
    history: list[Report] | None = None,
    dashboard_url: str | None = None,
) -> Path:
    """Generate a static V&V dashboard site.

    Parameters
    ----------
    spec:
        The specification being assessed.
    report:
        The current assessment report.
    output_dir:
        Directory to write the dashboard files into.
    history:
        Previous reports for version history tracking.
    dashboard_url:
        If set, the badge SVG links back to this URL.

    Returns
    -------
    Path
        The output directory.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    req_dir = output_dir / "requirements"
    req_dir.mkdir(exist_ok=True)

    # Build evidence lookup
    evidence_by_req: dict[str, list[Evidence]] = {}
    for ev in report.evidence:
        evidence_by_req.setdefault(ev.requirement_id, []).append(ev)

    # Build history lookup
    history_data = _build_all_history(spec, history or [])

    # Standards summary
    standards_info = _standards_summary(spec)

    # Generate badge
    export_badge(report, path=output_dir / "badge.svg", dashboard_url=dashboard_url)

    # Nav links
    nav = [("index.html", "Dashboard")]
    for req in spec.requirements:
        nav.append((f"requirements/{req.id}.html", req.id))

    # Generate index
    index_html = _render_index(spec, report, evidence_by_req, standards_info, history_data, nav)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    # Generate per-requirement pages
    for req in spec.requirements:
        ev_list = evidence_by_req.get(req.id, [])
        req_history = history_data.get(req.id, [])
        req_html = _render_requirement_page(req, ev_list, req_history, nav)
        (req_dir / f"{req.id}.html").write_text(req_html, encoding="utf-8")

    return output_dir


def _render_page(title: str, body: str, nav: list[tuple[str, str]], active: str = "") -> str:
    """Wrap body HTML in a full page with nav."""
    nav_html = ""
    for href, label in nav:
        cls = ' class="active"' if href == active else ""
        # Adjust relative paths for requirement subpages
        link = href if "/" not in active else f"../{href}"
        nav_html += f'<a href="{link}"{cls}>{_esc(label)}</a>\n'

    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{_esc(title)}</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n<body>\n"
        f'<header><div class="container"><h1>{_esc(title)}</h1></div></header>\n'
        f'<nav><div class="container">{nav_html}</div></nav>\n'
        f'<main class="container">{body}</main>\n'
        f'<div class="footer">Generated by <a href="https://github.com/ai-vnv/vnvspec">vnvspec</a>'
        f" v{_get_version()}</div>\n"
        "</body>\n</html>\n"
    )


def _render_index(
    spec: Spec,
    report: Report,
    evidence_by_req: dict[str, list[Evidence]],
    standards_info: list[dict[str, Any]],
    history_data: dict[str, list[dict[str, Any]]],
    nav: list[tuple[str, str]],
) -> str:
    """Render the main dashboard index page."""
    total = len(report.evidence)
    passed = report.pass_count()
    failed = report.fail_count()
    inconclusive = total - passed - failed
    verdict = report.verdict()
    covered = sum(1 for r in spec.requirements if r.id in evidence_by_req)

    # Version breakdown
    v01_reqs = [r for r in spec.requirements if r.metadata.get("since") == "0.1.0"]
    v02_reqs = [r for r in spec.requirements if r.metadata.get("since") == "0.2.0"]

    body = f"""
    <h2>Assessment Summary</h2>
    <div class="stats">
      <div class="stat"><div class="number pass">{passed}</div><div class="label">Passed</div></div>
      <div class="stat"><div class="number fail">{failed}</div><div class="label">Failed</div></div>
      <div class="stat"><div class="number inconclusive">{inconclusive}</div><div class="label">Inconclusive</div></div>
      <div class="stat"><div class="number">{len(spec.requirements)}</div><div class="label">Requirements</div></div>
    </div>
    <div class="card">
      <strong>Overall Verdict:</strong> <span class="{verdict}">{verdict.upper()}</span>
      &nbsp;|&nbsp; <strong>Spec:</strong> {_esc(spec.name)} v{_esc(spec.version)}
      &nbsp;|&nbsp; <strong>Assessed:</strong> {report.created_at.strftime("%Y-%m-%d %H:%M UTC")}
      &nbsp;|&nbsp; <strong>Coverage:</strong> {covered}/{len(spec.requirements)} requirements covered
    </div>

    <h2>Version Traceability</h2>
    <div class="card">
      <p><span class="tag tag-version">v0.1.0</span> {len(v01_reqs)} requirements &nbsp;
         <span class="tag tag-version">v0.2.0</span> {len(v02_reqs)} requirements</p>
    </div>
    """

    # Standards compliance section
    if standards_info:
        body += "\n<h2>Standards Compliance</h2>\n<table>\n"
        body += "<tr><th>Standard</th><th>Covered Clauses</th><th>Gaps</th><th>Coverage</th></tr>\n"
        for si in standards_info:
            total_c = si["total"]
            cov = si["covered"]
            pct = f"{cov / total_c * 100:.0f}%" if total_c > 0 else "N/A"
            color = "pass" if cov == total_c else "inconclusive" if cov > 0 else "fail"
            body += (
                f"<tr><td>{_esc(si['standard'])}</td>"
                f"<td>{cov}</td><td>{si['gaps']}</td>"
                f'<td><span class="{color}">{pct}</span></td></tr>\n'
            )
        body += "</table>\n"

    # Requirements table
    body += "\n<h2>Requirements</h2>\n<table>\n"
    body += "<tr><th>ID</th><th>Statement</th><th>Priority</th><th>Since</th><th>Verdict</th><th>Last Checked</th></tr>\n"
    for req in spec.requirements:
        ev_list = evidence_by_req.get(req.id, [])
        if ev_list:
            best = _best_verdict(ev_list)
            last_checked = max(e.observed_at for e in ev_list).strftime("%Y-%m-%d %H:%M")
        else:
            best = "inconclusive"
            last_checked = "—"
        since = req.metadata.get("since", "—")
        stmt = req.statement[:80] + "..." if len(req.statement) > 80 else req.statement
        body += (
            f'<tr><td><a href="requirements/{req.id}.html">{_esc(req.id)}</a></td>'
            f"<td>{_esc(stmt)}</td>"
            f'<td><span class="tag tag-{req.priority}">{req.priority}</span></td>'
            f'<td><span class="tag tag-version">{since}</span></td>'
            f'<td><span class="tag tag-{best}">{best}</span></td>'
            f"<td>{last_checked}</td></tr>\n"
        )
    body += "</table>\n"

    return _render_page(f"V&V Dashboard — {spec.name}", body, nav, active="index.html")


def _render_requirement_page(
    req: Requirement,
    evidence: list[Evidence],
    history_entries: list[dict[str, Any]],
    nav: list[tuple[str, str]],
) -> str:
    """Render a per-requirement detail page."""
    best = _best_verdict(evidence) if evidence else "inconclusive"
    since = req.metadata.get("since", "unknown")
    last_checked = (
        max(e.observed_at for e in evidence).strftime("%Y-%m-%d %H:%M UTC") if evidence else "Never"
    )

    body = f"""
    <div class="card">
      <h3>{_esc(req.id)} <span class="tag tag-{best}">{best}</span>
          <span class="tag tag-{req.priority}">{req.priority}</span>
          <span class="tag tag-version">since {since}</span></h3>
      <p><strong>Statement:</strong> {_esc(req.statement)}</p>
      <p><strong>Rationale:</strong> {_esc(req.rationale)}</p>
      <p><strong>Verification Method:</strong> {req.verification_method}</p>
      <p><strong>Last Checked:</strong> {last_checked}</p>
    </div>

    <h2>Acceptance Criteria</h2>
    <ul>
    """
    for criterion in req.acceptance_criteria:
        body += f"<li>{_esc(criterion)}</li>\n"
    body += "</ul>\n"

    # Standards mapping
    if req.standards:
        body += "\n<h2>Standards Mapping</h2>\n<table>\n"
        body += "<tr><th>Standard</th><th>Clauses</th></tr>\n"
        for std_name, clauses in req.standards.items():
            body += f"<tr><td>{_esc(std_name)}</td><td>{', '.join(clauses)}</td></tr>\n"
        body += "</table>\n"

    # Evidence
    body += "\n<h2>Evidence</h2>\n"
    if evidence:
        body += "<table>\n<tr><th>ID</th><th>Kind</th><th>Verdict</th><th>Observed</th><th>Details</th></tr>\n"
        for ev in sorted(evidence, key=lambda e: e.observed_at, reverse=True):
            details = ", ".join(f"{k}: {v}" for k, v in ev.details.items()) if ev.details else "—"
            body += (
                f"<tr><td>{_esc(ev.id)}</td>"
                f"<td>{ev.kind}</td>"
                f'<td><span class="tag tag-{ev.verdict}">{ev.verdict}</span></td>'
                f"<td>{ev.observed_at.strftime('%Y-%m-%d %H:%M')}</td>"
                f"<td>{_esc(details)}</td></tr>\n"
            )
        body += "</table>\n"
    else:
        body += '<p class="inconclusive">No evidence collected for this requirement.</p>\n'

    # Version history
    if history_entries:
        body += '\n<h2>Version History</h2>\n<div class="timeline">\n'
        for entry in history_entries:
            v = entry["verdict"]
            body += (
                f'<div class="timeline-entry">'
                f'<span class="tag tag-version">{_esc(entry["version"])}</span> '
                f'<span class="tag tag-{v}">{v}</span> '
                f"{entry['checked_at']}"
                f"</div>\n"
            )
        body += "</div>\n"

    return _render_page(
        f"{req.id} — {req.statement[:50]}",
        body,
        nav,
        active=f"requirements/{req.id}.html",
    )


def _standards_summary(spec: Spec) -> list[dict[str, Any]]:
    """Collect standards coverage from all requirements."""
    from vnvspec.core.trace import standard_gap_analysis  # noqa: PLC0415

    # Find all referenced standards
    std_names: set[str] = set()
    for req in spec.requirements:
        std_names.update(req.standards.keys())

    results = []
    for name in sorted(std_names):
        try:
            gap = standard_gap_analysis(spec, name)
            results.append(
                {
                    "standard": gap.standard,
                    "total": gap.total_clauses,
                    "covered": gap.covered,
                    "gaps": gap.gaps,
                }
            )
        except Exception:
            pass
    return results


def _build_all_history(spec: Spec, history: list[Report]) -> dict[str, list[dict[str, Any]]]:
    """Build version history per requirement from historical reports."""
    result: dict[str, list[dict[str, Any]]] = {}
    for report in history:
        for req in spec.requirements:
            ev_list = [e for e in report.evidence if e.requirement_id == req.id]
            if ev_list:
                verdict = _best_verdict(ev_list)
                checked_at = max(e.observed_at for e in ev_list).strftime("%Y-%m-%d")
            else:
                verdict = "inconclusive"
                checked_at = report.created_at.strftime("%Y-%m-%d")
            result.setdefault(req.id, []).append(
                {
                    "version": report.spec_version or "?",
                    "verdict": verdict,
                    "checked_at": checked_at,
                }
            )
    return result


def _best_verdict(evidence: list[Evidence]) -> str:
    """Worst-case verdict: if any fail → fail, any inconclusive → inconclusive, else pass."""
    if any(e.verdict == "fail" for e in evidence):
        return "fail"
    if any(e.verdict == "inconclusive" for e in evidence):
        return "inconclusive"
    return "pass"


def _esc(text: str) -> str:
    """HTML-escape text."""
    return html_lib.escape(text)


def _get_version() -> str:
    """Get vnvspec version."""
    from vnvspec._version import __version__  # noqa: PLC0415

    return __version__
