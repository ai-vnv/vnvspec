"""Report diff — compare two assessment reports for regressions.

Identifies new failures, new passes, regressions, and requirement changes
between two reports.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from vnvspec.core.assessment import Report


class ReportDiff(BaseModel):
    """Differences between two assessment reports."""

    model_config = {"frozen": True}

    new_failures: list[str] = Field(
        default_factory=list,
        description="Requirement IDs that newly failed (pass/inconclusive → fail).",
    )
    new_passes: list[str] = Field(
        default_factory=list,
        description="Requirement IDs that newly passed (fail/inconclusive → pass).",
    )
    regressions: list[str] = Field(
        default_factory=list,
        description="Requirement IDs that regressed (pass → fail).",
    )
    removed_requirements: list[str] = Field(
        default_factory=list,
        description="Requirement IDs present in previous but not current.",
    )
    added_requirements: list[str] = Field(
        default_factory=list,
        description="Requirement IDs present in current but not previous.",
    )


def compare_reports(previous: Report, current: Report) -> ReportDiff:
    """Compare two reports and identify differences.

    Parameters
    ----------
    previous:
        The baseline report.
    current:
        The new report to compare against baseline.

    Returns
    -------
    ReportDiff
        Structured differences between the two reports.
    """
    # Build per-requirement verdict maps (best verdict wins if multiple evidence)
    prev_verdicts = _best_verdicts(previous)
    curr_verdicts = _best_verdicts(current)

    prev_ids = set(prev_verdicts.keys())
    curr_ids = set(curr_verdicts.keys())

    new_failures: list[str] = []
    new_passes: list[str] = []
    regressions: list[str] = []

    for req_id in sorted(prev_ids & curr_ids):
        prev_v = prev_verdicts[req_id]
        curr_v = curr_verdicts[req_id]
        if prev_v != "fail" and curr_v == "fail":
            new_failures.append(req_id)
            if prev_v == "pass":
                regressions.append(req_id)
        elif prev_v != "pass" and curr_v == "pass":
            new_passes.append(req_id)

    return ReportDiff(
        new_failures=new_failures,
        new_passes=new_passes,
        regressions=regressions,
        removed_requirements=sorted(prev_ids - curr_ids),
        added_requirements=sorted(curr_ids - prev_ids),
    )


def _best_verdicts(report: Report) -> dict[str, str]:
    """Extract best verdict per requirement (pass > inconclusive > fail)."""
    rank = {"pass": 2, "inconclusive": 1, "fail": 0}
    best: dict[str, str] = {}
    for ev in report.evidence:
        current = best.get(ev.requirement_id)
        if current is None or rank.get(ev.verdict, 0) > rank.get(current, 0):
            best[ev.requirement_id] = ev.verdict
    return best
