"""EvidenceCollector — ergonomic context manager for building Evidence.

Usage::

    from vnvspec.collectors import EvidenceCollector

    with EvidenceCollector(spec) as collector:
        collector.check("REQ-001", accuracy > 0.9, message="accuracy check")
        collector.record("REQ-002", "pass", message="manual review done")
    report = collector.build_report(summary="all checks passed")
"""

from __future__ import annotations

import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Self

from vnvspec.core.assessment import Report
from vnvspec.core.errors import RequirementError
from vnvspec.core.evidence import Evidence, EvidenceKind, Verdict
from vnvspec.core.spec import Spec


class EvidenceCollector:
    """Context manager for collecting :class:`Evidence` against a :class:`Spec`.

    Parameters
    ----------
    spec:
        The spec whose requirements evidence is collected for.
    default_kind:
        Default evidence kind when not specified per-call.

    Example::

        with EvidenceCollector(spec) as c:
            c.check("REQ-001", result > threshold, message="threshold met")
        report = c.build_report()
    """

    def __init__(self, spec: Spec, *, default_kind: EvidenceKind = "test") -> None:
        self._spec = spec
        self._default_kind = default_kind
        self._evidence: list[Evidence] = []
        self._counter = 0

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        pass

    def _next_id(self) -> str:
        self._counter += 1
        return f"EV-AUTO-{self._counter:04d}"

    def _validate_requirement(self, requirement_id: str) -> None:
        """Ensure the requirement_id exists in the spec."""
        req_ids = {r.id for r in self._spec.requirements}
        if requirement_id not in req_ids:
            raise RequirementError(
                f"Requirement '{requirement_id}' not found in spec '{self._spec.name}'. "
                f"Available: {sorted(req_ids)}"
            )

    def check(
        self,
        requirement_id: str,
        condition: bool,
        message: str = "",
        **details: Any,
    ) -> Evidence:
        """Record evidence based on a boolean condition.

        Parameters
        ----------
        requirement_id:
            Must match an existing requirement in the spec.
        condition:
            ``True`` → pass, ``False`` → fail.
        message:
            Human-readable description.
        **details:
            Additional metadata merged into ``Evidence.details``.

        Returns
        -------
        Evidence
            The recorded evidence object.
        """
        self._validate_requirement(requirement_id)
        verdict: Verdict = "pass" if condition else "fail"
        detail_dict: dict[str, Any] = {**details}
        if message:
            detail_dict["message"] = message
        ev = Evidence(
            id=self._next_id(),
            requirement_id=requirement_id,
            kind=self._default_kind,
            verdict=verdict,
            details=detail_dict,
        )
        self._evidence.append(ev)
        return ev

    def record(
        self,
        requirement_id: str,
        verdict: Verdict,
        *,
        kind: EvidenceKind | None = None,
        message: str = "",
        **details: Any,
    ) -> Evidence:
        """Record evidence with an explicit verdict.

        Parameters
        ----------
        requirement_id:
            Must match an existing requirement in the spec.
        verdict:
            One of ``"pass"``, ``"fail"``, ``"inconclusive"``.
        kind:
            Override the default evidence kind.
        message:
            Human-readable description.
        **details:
            Additional metadata merged into ``Evidence.details``.

        Returns
        -------
        Evidence
            The recorded evidence object.
        """
        self._validate_requirement(requirement_id)
        detail_dict: dict[str, Any] = {**details}
        if message:
            detail_dict["message"] = message
        ev = Evidence(
            id=self._next_id(),
            requirement_id=requirement_id,
            kind=kind or self._default_kind,
            verdict=verdict,
            details=detail_dict,
        )
        self._evidence.append(ev)
        return ev

    def from_pytest_junit(
        self,
        path: Path | str,
        *,
        requirement_marker: str = "vnvspec",
    ) -> list[Evidence]:
        """Parse a JUnit XML report and extract evidence.

        Each ``<testcase>`` element whose ``classname`` or ``name`` contains
        a property with the given *requirement_marker* key is converted to
        an :class:`Evidence` object.

        The marker value should be the requirement ID (e.g.
        ``@pytest.mark.vnvspec("REQ-001")``). In JUnit XML this appears
        as a ``<property name="vnvspec" value="REQ-001" />`` child.

        Parameters
        ----------
        path:
            Path to the JUnit XML file.
        requirement_marker:
            Property name to look for in test case properties.

        Returns
        -------
        list[Evidence]
            Evidence objects for each matched test case.
        """
        path = Path(path)
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            raise RequirementError(f"Failed to parse JUnit XML at {path}: {exc}") from exc

        root = tree.getroot()
        results: list[Evidence] = []

        # Handle both <testsuite> and <testsuites> root elements
        testcases = root.iter("testcase")
        for tc in testcases:
            # Look for vnvspec property
            props = tc.find("properties")
            if props is None:
                continue
            req_id: str | None = None
            for prop in props.findall("property"):
                if prop.get("name") == requirement_marker:
                    req_id = prop.get("value", "")
                    break
            if not req_id:
                continue

            # Determine verdict
            verdict: Verdict
            if tc.find("failure") is not None:
                verdict = "fail"
            elif tc.find("skipped") is not None:
                verdict = "inconclusive"
            elif tc.find("error") is not None:
                verdict = "fail"
            else:
                verdict = "pass"

            name = tc.get("name", "unknown")
            classname = tc.get("classname", "")

            # Validate requirement exists (skip with warning if not)
            req_ids = {r.id for r in self._spec.requirements}
            if req_id not in req_ids:
                warnings.warn(
                    f"JUnit test '{name}' references unknown requirement '{req_id}', skipping.",
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue

            ev = Evidence(
                id=self._next_id(),
                requirement_id=req_id,
                kind="test",
                verdict=verdict,
                details={
                    "source": "pytest-junit",
                    "test_name": name,
                    "classname": classname,
                },
            )
            self._evidence.append(ev)
            results.append(ev)

        return results

    def build_report(self, *, summary: str | dict[str, Any] | None = None) -> Report:
        """Build a :class:`Report` from the collected evidence.

        Parameters
        ----------
        summary:
            Optional summary (str or dict). Strings are auto-wrapped.
        """
        report_kwargs: dict[str, Any] = {
            "spec_name": self._spec.name,
            "spec_version": self._spec.version,
            "evidence": list(self._evidence),
        }
        if summary is None:
            report_kwargs["summary"] = {
                "total": len(self._evidence),
                "pass": sum(1 for e in self._evidence if e.verdict == "pass"),
                "fail": sum(1 for e in self._evidence if e.verdict == "fail"),
                "inconclusive": sum(1 for e in self._evidence if e.verdict == "inconclusive"),
            }
        else:
            report_kwargs["summary"] = summary
        return Report(**report_kwargs)
