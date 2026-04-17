"""pytest-vnvspec plugin — captures V&V evidence from test results.

Registers:
- ``pytest.mark.vnvspec(requirement_id)`` marker
- ``--vnvspec-spec`` CLI option
- ``--vnvspec-report`` CLI option
- ``--vnvspec-fail-on`` CLI option
"""

from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence
from vnvspec.core.spec import Spec


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register vnvspec CLI options."""
    group = parser.getgroup("vnvspec", "V&V specification evidence capture")
    group.addoption(
        "--vnvspec-spec",
        dest="vnvspec_spec",
        default=None,
        help="Path to vnvspec spec file (YAML, TOML, or JSON).",
    )
    group.addoption(
        "--vnvspec-report",
        dest="vnvspec_report",
        default=None,
        help="Output path for the vnvspec assessment report (JSON).",
    )
    group.addoption(
        "--vnvspec-fail-on",
        dest="vnvspec_fail_on",
        default="never",
        choices=["any", "blocking", "never"],
        help="When to fail: 'any' (any fail verdict), 'blocking' (only blocking reqs), 'never'.",
    )


def _load_spec(spec_path: str) -> Spec:
    """Load spec from file, detecting format by extension."""
    path = Path(spec_path)
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return Spec.from_yaml(path)
    if suffix == ".toml":
        return Spec.from_toml(path)
    if suffix == ".json":
        return Spec.from_json(path)
    # Fallback: try JSON then YAML
    try:
        return Spec.from_json(path)
    except Exception:
        return Spec.from_yaml(path)


def pytest_configure(config: pytest.Config) -> None:
    """Register marker and plugin if spec is provided."""
    config.addinivalue_line(
        "markers",
        "vnvspec(requirement_id): link this test to a vnvspec requirement.",
    )
    spec_path = config.getoption("vnvspec_spec", default=None)
    if spec_path is not None:
        spec = _load_spec(spec_path)
        plugin = VnvspecPlugin(spec)
        config.pluginmanager.register(plugin, "vnvspec-plugin")


class VnvspecPlugin:
    """Core plugin that collects evidence during test execution."""

    def __init__(self, spec: Spec) -> None:
        self.spec = spec
        self.evidence: list[Evidence] = []
        self._counter = 0
        self._req_ids = {r.id for r in spec.requirements}
        self._seen_req_ids: set[str] = set()

    def _next_id(self) -> str:
        self._counter += 1
        return f"EV-PYTEST-{self._counter:04d}"

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(
        self,
        config: pytest.Config,
        items: list[pytest.Item],
    ) -> None:
        """Validate marker references against spec at collection time."""
        for item in items:
            for marker in item.iter_markers("vnvspec"):
                if marker.args:
                    req_id = marker.args[0]
                    if req_id not in self._req_ids:
                        warnings.warn(
                            f"Test '{item.nodeid}' references unknown requirement "
                            f"'{req_id}' — evidence will not be captured.",
                            pytest.PytestUnknownMarkWarning,
                            stacklevel=1,
                        )

    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_makereport(
        self,
        item: pytest.Item,
        call: pytest.CallInfo[None],
    ) -> None:
        """Capture verdict after each test phase."""
        if call.when != "call":
            return

        for marker in item.iter_markers("vnvspec"):
            if not marker.args:
                continue
            req_id = marker.args[0]
            if req_id not in self._req_ids:
                continue

            self._seen_req_ids.add(req_id)
            verdict = "fail" if call.excinfo is not None else "pass"

            ev = Evidence(
                id=self._next_id(),
                requirement_id=req_id,
                kind="test",
                verdict=verdict,
                details={
                    "source": "pytest-vnvspec",
                    "nodeid": item.nodeid,
                    "test_name": item.name,
                },
            )
            self.evidence.append(ev)

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        """Build report and emit at session end."""
        # Add inconclusive evidence for test requirements with no matching tests
        for req in self.spec.requirements:
            if req.verification_method == "test" and req.id not in self._seen_req_ids:
                ev = Evidence(
                    id=self._next_id(),
                    requirement_id=req.id,
                    kind="test",
                    verdict="inconclusive",
                    details={
                        "source": "pytest-vnvspec",
                        "reason": "no test linked",
                    },
                )
                self.evidence.append(ev)

        report = Report(
            spec_name=self.spec.name,
            spec_version=self.spec.version,
            evidence=self.evidence,
            summary={
                "total": len(self.evidence),
                "pass": sum(1 for e in self.evidence if e.verdict == "pass"),
                "fail": sum(1 for e in self.evidence if e.verdict == "fail"),
                "inconclusive": sum(1 for e in self.evidence if e.verdict == "inconclusive"),
            },
        )

        # Write report if path specified
        report_path = session.config.getoption("vnvspec_report")
        if report_path:
            path = Path(report_path)
            path.write_text(report.model_dump_json(indent=2), encoding="utf-8")

        # Store report on session for programmatic access
        session.config._vnvspec_report = report  # type: ignore[attr-defined]

        # Check fail-on policy
        fail_on = session.config.getoption("vnvspec_fail_on")
        if fail_on == "any" and report.fail_count() > 0:
            session.exitstatus = pytest.ExitCode.TESTS_FAILED
        elif fail_on == "blocking":
            blocking_ids = {r.id for r in self.spec.requirements if r.priority == "blocking"}
            blocking_fails = [
                e for e in self.evidence if e.verdict == "fail" and e.requirement_id in blocking_ids
            ]
            if blocking_fails:
                session.exitstatus = pytest.ExitCode.TESTS_FAILED
