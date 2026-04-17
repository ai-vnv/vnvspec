"""Badge exporter — generates V&V status badge as SVG.

Produces a locally-generated SVG badge with no external service dependency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from vnvspec.core.assessment import Report

_COLORS = {
    "pass": "#4c1",
    "fail": "#e05d44",
    "inconclusive": "#dfb317",
}

_BADGE_TEMPLATE = """\
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" \
aria-label="V&amp;V: {text}">
  <title>V&amp;V: {text}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{width}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{color}"/>
    <rect width="{width}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" \
font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" \
font-size="11">
    <text aria-hidden="true" x="{label_x}" y="15" fill="#010101" fill-opacity=".3">\
{label}</text>
    <text x="{label_x}" y="14">{label}</text>
    <text aria-hidden="true" x="{value_x}" y="15" fill="#010101" fill-opacity=".3">\
{text}</text>
    <text x="{value_x}" y="14">{text}</text>
  </g>
</svg>"""


def export_badge(
    report: Report,
    *,
    path: Path | str,
    style: Literal["flat", "for-the-badge"] = "flat",
    dashboard_url: str | None = None,
) -> Path:
    """Generate a V&V status badge as SVG.

    Parameters
    ----------
    report:
        Assessment report.
    path:
        Output SVG file path.
    style:
        Badge style (currently ``"flat"`` only; ``"for-the-badge"`` reserved).

    Returns
    -------
    Path
        The written SVG file path.
    """
    path = Path(path)
    total = len(report.evidence)
    passed = report.pass_count()
    failed = report.fail_count()

    inconclusive = sum(1 for e in report.evidence if e.verdict == "inconclusive")

    if failed > 0:
        verdict = "fail"
        text = f"{passed}/{total} FAIL"
    elif total == 0:
        verdict = "inconclusive"
        text = "N/A"
    elif inconclusive > 0:
        verdict = "inconclusive"
        text = f"{passed}/{total} INCONCLUSIVE"
    else:
        verdict = "pass"
        text = f"{passed}/{total} PASS"

    color = _COLORS[verdict]
    label = "V&V"
    label_width = 32
    value_width = max(len(text) * 7 + 10, 50)
    width = label_width + value_width
    label_x = label_width / 2
    value_x = label_width + value_width / 2

    svg = _BADGE_TEMPLATE.format(
        width=width,
        label_width=label_width,
        value_width=value_width,
        label_x=label_x,
        value_x=value_x,
        label=label,
        text=text,
        color=color,
    )

    if dashboard_url:
        svg = svg.replace(
            "<g clip-path",
            f'<a href="{dashboard_url}" target="_blank"><g clip-path',
        ).replace("</svg>", "</a>\n</svg>")

    path.write_text(svg, encoding="utf-8")
    return path
