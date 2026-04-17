"""JSON exporter."""

from __future__ import annotations

import json
from pathlib import Path

from vnvspec.core.assessment import Report


def export_json(report: Report, path: Path | None = None) -> str:
    """Export *report* as a JSON string.

    If *path* is given the JSON is also written to that file.

    Example:
        >>> from vnvspec.core.assessment import Report
        >>> j = export_json(Report(spec_name="demo", spec_version="1.0"))
        >>> '"spec_name"' in j
        True
    """
    data = json.loads(report.model_dump_json())
    text = json.dumps(data, indent=2, ensure_ascii=False)

    if path is not None:
        path.write_text(text, encoding="utf-8")

    return text
