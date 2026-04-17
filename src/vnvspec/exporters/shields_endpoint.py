"""Shields.io endpoint exporter — generates JSON for dynamic badges.

Produces a JSON file conforming to the Shields.io endpoint badge API
(https://shields.io/endpoint). The file can be hosted on GitHub Pages
and referenced via:

    https://img.shields.io/endpoint?url=https://<user>.github.io/<repo>/vnv-badge.json

Color logic:
- green: all evidence passes
- yellow: any inconclusive, no failures
- red: any failure
- lightgrey: no evidence
"""

from __future__ import annotations

import json
from pathlib import Path

from vnvspec.core.assessment import Report


def export_shields_endpoint(
    report: Report,
    *,
    path: Path | str,
    label: str = "V&V",
) -> Path:
    """Write a Shields.io endpoint JSON file.

    Parameters
    ----------
    report:
        Assessment report.
    path:
        Output JSON file path.
    label:
        Badge label text (default: "V&V").

    Returns
    -------
    Path
        The written JSON file path.
    """
    path = Path(path)
    total = len(report.evidence)
    passed = report.pass_count()
    failed = report.fail_count()
    inconclusive = report.inconclusive_count()

    if failed > 0:
        message = f"{passed}/{total} ({failed} failed)"
        color = "red"
    elif total == 0:
        message = "no evidence"
        color = "lightgrey"
    elif inconclusive > 0:
        message = f"{passed}/{total} ({inconclusive} inconclusive)"
        color = "yellow"
    else:
        message = f"{passed}/{total} pass"
        color = "green"

    endpoint = {
        "schemaVersion": 1,
        "label": label,
        "message": message,
        "color": color,
    }

    path.write_text(json.dumps(endpoint, indent=2) + "\n", encoding="utf-8")
    return path
