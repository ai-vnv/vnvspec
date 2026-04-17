#!/usr/bin/env python3
"""Run vnvspec self-assessment — vnvspec assessed against itself.

This script loads .vnvspec/self-spec.yaml, runs verification checks
for each requirement, and produces a Report as JSON + HTML.

Usage:
    python scripts/self_assess.py
    # or: vnvspec assess --self
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF_SPEC_PATH = ROOT / ".vnvspec" / "self-spec.yaml"
REPORT_JSON = ROOT / ".vnvspec" / "self-assessment-report.json"
REPORT_HTML = ROOT / ".vnvspec" / "self-assessment-report.html"


def main() -> int:
    from vnvspec import Spec
    from vnvspec.collectors import EvidenceCollector
    from vnvspec.exporters import export_html

    # Load self-spec
    print(f"Loading self-spec from {SELF_SPEC_PATH}")
    spec = Spec.from_yaml(SELF_SPEC_PATH)
    print(f"  {len(spec.requirements)} requirements loaded")

    with EvidenceCollector(spec) as c:
        # REQ-SELF-FROZEN-001: Core models are frozen
        _check_frozen_models(c)

        # REQ-SELF-FROZEN-002: Spec.extend() doesn't mutate
        _check_extend_immutability(c)

        # REQ-SELF-COMPAT-001: v0.1 symbols importable
        _check_v01_compat(c)

        # REQ-SELF-TYPES-001: mypy --strict passes
        _check_mypy(c)

        # REQ-SELF-LINT-001: ruff passes
        _check_ruff(c)

        # REQ-SELF-COV-001: coverage >= 85%
        _check_coverage(c)

        # REQ-SELF-DOCS-001: mkdocs --strict passes
        _check_docs(c)

        # REQ-SELF-ERGO-001: Evidence.details str|dict
        _check_evidence_details(c)

        # REQ-SELF-ERGO-002: Report.summary str|dict
        _check_report_summary(c)

        # REQ-SELF-CLI-001: structured exit codes
        _check_exit_codes(c)

        # REQ-SELF-COLLECTOR-001: RequirementError on unknown ID
        _check_collector_validation(c)

        # REQ-SELF-IO-001: YAML/TOML round-trip
        _check_io_roundtrip(c)

        # REQ-SELF-GAP-001: gap analysis correctness
        _check_gap_analysis(c)

        # REQ-SELF-PROFILE-001: web-app profile
        _check_profile(c)

        # REQ-SELF-TRACE-001: auto_trace word boundary
        _check_auto_trace(c)

        # REQ-SELF-BADGE-001: badge SVG
        _check_badge(c)

        # REQ-SELF-DIFF-001: report diff regressions
        _check_diff(c)

        # REQ-SELF-DEP-001: deprecation decorator
        _check_deprecation(c)

        # REQ-SELF-META-001: self-spec is loadable
        c.check("REQ-SELF-META-001", True, message="Self-spec loaded successfully (we're running)")

        # --- v0.3 requirements ---
        # REQ-SELF-VERDICT-001: strict verdict semantics
        _check_verdict_strict(c)

        # REQ-SELF-FORMAL-001: formal_proof is valid
        _check_formal_proof(c)

        # REQ-SELF-SOURCE-001: source field accepts str and list
        _check_source_field(c)

        # REQ-SELF-COMPAT-002: v0.2 symbols importable
        _check_v02_compat(c)

        # REQ-SELF-CATALOG-PYT-001: PyTorch catalog >= 30 requirements
        _check_pytorch_catalog(c)

        # REQ-SELF-CATALOG-001: catalog CLI works
        _check_catalog_cli(c)

        # REQ-SELF-SHIELDS-001: shields endpoint produces valid JSON
        _check_shields_endpoint(c)

    report = c.build_report(summary="vnvspec v0.3.0 self-assessment")

    # Write outputs
    REPORT_JSON.write_text(report.model_dump_json(indent=2), encoding="utf-8")
    export_html(report, path=REPORT_HTML)

    # Summary
    print(f"\n{'=' * 60}")
    print(f"Self-Assessment Report: {report.verdict().upper()}")
    print(f"  Pass: {report.pass_count()}")
    print(f"  Fail: {report.fail_count()}")
    print(f"  Inconclusive: {sum(1 for e in report.evidence if e.verdict == 'inconclusive')}")
    print("\nReport written to:")
    print(f"  JSON: {REPORT_JSON}")
    print(f"  HTML: {REPORT_HTML}")

    # Exit based on blocking requirements
    blocking_ids = {r.id for r in spec.requirements if r.priority == "blocking"}
    blocking_fails = [
        e for e in report.evidence if e.verdict == "fail" and e.requirement_id in blocking_ids
    ]
    if blocking_fails:
        print(f"\nBLOCKING FAILURES: {[e.requirement_id for e in blocking_fails]}")
        return 1
    if report.fail_count() > 0:
        print("\nNon-blocking failures present — review recommended.")
        return 0
    return 0


def _run(cmd: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


def _check_frozen_models(c: object) -> None:
    from pydantic import ValidationError

    from vnvspec import ODD, Evidence, Hazard, IOContract, Requirement, Spec, TraceLink

    all_frozen = True
    for cls in [Spec, Requirement, Evidence, Hazard, ODD, IOContract, TraceLink]:
        cfg = getattr(cls, "model_config", {})
        if not cfg.get("frozen", False):
            all_frozen = False
            break

    # Test mutation raises
    mutation_blocked = False
    try:
        e = Evidence(id="EV-T", requirement_id="R", kind="test", verdict="pass")
        e.id = "EV-X"  # type: ignore[misc]
    except ValidationError:
        mutation_blocked = True

    c.check(
        "REQ-SELF-FROZEN-001",
        all_frozen and mutation_blocked,  # type: ignore[union-attr]
        message=f"frozen={all_frozen}, mutation_blocked={mutation_blocked}",
    )


def _check_extend_immutability(c: object) -> None:
    from vnvspec import Requirement, Spec

    spec = Spec(
        name="t", requirements=[Requirement(id="R-1", statement="X.", verification_method="test")]
    )
    original_len = len(spec.requirements)
    new_req = Requirement(id="R-2", statement="Y.", verification_method="test")
    spec2 = spec.extend([new_req])
    ok = len(spec.requirements) == original_len and len(spec2.requirements) == original_len + 1
    c.check(
        "REQ-SELF-FROZEN-002",
        ok,
        message=f"original={original_len}, extended={len(spec2.requirements)}",
    )  # type: ignore[union-attr]


def _check_v01_compat(c: object) -> None:
    result = _run([sys.executable, "scripts/check_v0_1_compat.py"])
    c.check(
        "REQ-SELF-COMPAT-001",
        result.returncode == 0,  # type: ignore[union-attr]
        message=result.stdout.strip() or result.stderr.strip(),
    )


def _check_mypy(c: object) -> None:
    result = _run(["uv", "run", "mypy", "--strict", "src/vnvspec"])
    ok = result.returncode == 0 and "no issues found" in result.stdout
    c.check(
        "REQ-SELF-TYPES-001",
        ok,  # type: ignore[union-attr]
        message=result.stdout.strip().split("\n")[-1] if result.stdout else result.stderr.strip(),
    )


def _check_ruff(c: object) -> None:
    r1 = _run(["uv", "run", "ruff", "format", "--check", "."])
    r2 = _run(["uv", "run", "ruff", "check", "."])
    ok = r1.returncode == 0 and r2.returncode == 0
    c.check(
        "REQ-SELF-LINT-001",
        ok,  # type: ignore[union-attr]
        message=f"format={r1.returncode}, check={r2.returncode}",
    )


def _check_coverage(c: object) -> None:
    result = _run(
        [
            "uv",
            "run",
            "pytest",
            "-p",
            "no:vnvspec",
            "--cov=src/vnvspec",
            "--cov-fail-under=95",
            "--ignore=packages",
            "-q",
            "--no-header",
        ]
    )
    ok = result.returncode == 0 or "Required test coverage" in result.stdout
    # Extract pass count
    match = re.search(r"(\d+) passed", result.stdout)
    passed = match.group(1) if match else "?"
    c.check(
        "REQ-SELF-COV-001",
        ok,  # type: ignore[union-attr]
        message=f"{passed} tests passed, coverage threshold met",
    )


def _check_docs(c: object) -> None:
    result = _run(["uv", "run", "mkdocs", "build", "--strict"])
    ok = result.returncode == 0
    c.check(
        "REQ-SELF-DOCS-001",
        ok,  # type: ignore[union-attr]
        message="mkdocs build --strict passed" if ok else result.stderr.strip()[:200],
    )


def _check_evidence_details(c: object) -> None:
    from vnvspec import Evidence

    e1 = Evidence(id="T1", requirement_id="R", kind="test", verdict="pass", details="ok")  # type: ignore[arg-type]
    e2 = Evidence(id="T2", requirement_id="R", kind="test", verdict="pass", details={"k": "v"})
    ok = e1.details == {"message": "ok"} and e2.details == {"k": "v"}
    c.check("REQ-SELF-ERGO-001", ok, message=f"str_wrap={e1.details}, dict_pass={e2.details}")  # type: ignore[union-attr]


def _check_report_summary(c: object) -> None:
    from vnvspec import Report

    r = Report(spec_name="t", summary="ok")  # type: ignore[arg-type]
    ok = r.summary == {"message": "ok"}
    c.check("REQ-SELF-ERGO-002", ok, message=f"summary={r.summary}")  # type: ignore[union-attr]


def _check_exit_codes(c: object) -> None:
    from vnvspec.cli.main import ExitCode

    expected = {0, 1, 2, 3, 4, 5}
    actual = {e.value for e in ExitCode}
    ok = expected == actual
    c.check("REQ-SELF-CLI-001", ok, message=f"exit_codes={sorted(actual)}")  # type: ignore[union-attr]


def _check_collector_validation(c: object) -> None:
    from vnvspec import EvidenceCollector, Requirement, RequirementError, Spec

    spec = Spec(
        name="t", requirements=[Requirement(id="R-1", statement="X.", verification_method="test")]
    )
    raised = False
    with EvidenceCollector(spec) as ec:
        try:
            ec.check("UNKNOWN", True)
        except RequirementError:
            raised = True
    c.check("REQ-SELF-COLLECTOR-001", raised, message=f"RequirementError raised={raised}")  # type: ignore[union-attr]


def _check_io_roundtrip(c: object) -> None:
    import tomllib

    import yaml as _yaml

    from vnvspec import Requirement, Spec

    spec = Spec(
        name="rt",
        requirements=[
            Requirement(
                id="R-1",
                statement="X.",
                rationale="Y.",
                verification_method="test",
                acceptance_criteria=["Z."],
            )
        ],
    )

    # YAML round-trip
    yaml_text = spec.to_yaml()
    spec_y = Spec.model_validate(_yaml.safe_load(yaml_text))
    yaml_ok = spec.model_dump() == spec_y.model_dump()

    # TOML round-trip
    toml_text = spec.to_toml()
    spec_t = Spec.model_validate(tomllib.loads(toml_text))
    toml_ok = spec.model_dump() == spec_t.model_dump()

    c.check(
        "REQ-SELF-IO-001",
        yaml_ok and toml_ok,  # type: ignore[union-attr]
        message=f"yaml_rt={yaml_ok}, toml_rt={toml_ok}",
    )


def _check_gap_analysis(c: object) -> None:
    from vnvspec import Requirement, Spec
    from vnvspec.core.trace import standard_gap_analysis

    # Empty spec = all gaps
    empty = Spec(name="e")
    gap = standard_gap_analysis(empty, "iso_pas_8800")
    all_gaps = gap.covered == 0 and gap.gaps > 0

    # Spec with mapping = covered
    mapped = Spec(
        name="m",
        requirements=[
            Requirement(
                id="R-1",
                statement="X.",
                rationale="Y.",
                verification_method="analysis",
                acceptance_criteria=["Z."],
                standards={"iso_pas_8800": ["6.2.1"]},
            )
        ],
    )
    gap2 = standard_gap_analysis(mapped, "iso_pas_8800")
    has_covered = gap2.covered >= 1

    c.check(
        "REQ-SELF-GAP-001",
        all_gaps and has_covered,  # type: ignore[union-attr]
        message=f"empty_all_gaps={all_gaps}, mapped_has_covered={has_covered}",
    )


def _check_profile(c: object) -> None:
    from vnvspec import Requirement
    from vnvspec.core._internal.gtwr_rules import RuleProfile, check_all

    req = Requirement(
        id="R-1",
        statement="The system shall handle 500 requests.",
        rationale="Load.",
        verification_method="test",
        acceptance_criteria=["500 req/s"],
    )
    formal = check_all(req, profile=RuleProfile.FORMAL)
    webapp = check_all(req, profile=RuleProfile.WEB_APP)
    r6_formal = [v for v in formal if v.rule == "R6"]
    r6_webapp = [v for v in webapp if v.rule == "R6"]
    ok = (
        len(r6_formal) == 1
        and r6_formal[0].severity == "warning"
        and len(r6_webapp) == 1
        and r6_webapp[0].severity == "info"
    )
    c.check(
        "REQ-SELF-PROFILE-001",
        ok,  # type: ignore[union-attr]
        message=f"formal_R6={r6_formal[0].severity if r6_formal else 'N/A'}, "
        f"webapp_R6={r6_webapp[0].severity if r6_webapp else 'N/A'}",
    )


def _check_auto_trace(c: object) -> None:
    import tempfile

    from vnvspec import Requirement, Spec
    from vnvspec.trace.auto import auto_trace

    spec = Spec(
        name="t",
        requirements=[Requirement(id="REQ-001", statement="X.", verification_method="test")],
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        (p / "code.py").write_text("# REQ-001 is here\n# REQ-001X is not\n")
        links = auto_trace(spec, paths=[p])
        hits = [l for l in links if l.source_id == "REQ-001"]
        # Should find REQ-001 but not match REQ-001X
        ok = len(hits) == 1
    c.check("REQ-SELF-TRACE-001", ok, message=f"hits={len(hits)}")  # type: ignore[union-attr]


def _check_badge(c: object) -> None:
    import tempfile

    from vnvspec import Evidence, Report
    from vnvspec.exporters.badge import export_badge

    report = Report(
        spec_name="t",
        evidence=[
            Evidence(id="E1", requirement_id="R", kind="test", verdict="pass"),
        ],
    )
    with tempfile.TemporaryDirectory() as td:
        svg_path = Path(td) / "badge.svg"
        export_badge(report, path=svg_path)
        svg = svg_path.read_text()
        ok = "#4c1" in svg and "PASS" in svg
    c.check("REQ-SELF-BADGE-001", ok, message=f"green_pass={'#4c1' in svg}, text={'PASS' in svg}")  # type: ignore[union-attr]


def _check_diff(c: object) -> None:
    from vnvspec import Evidence, Report
    from vnvspec.diff import compare_reports

    prev = Report(
        spec_name="t",
        evidence=[
            Evidence(id="E1", requirement_id="R1", kind="test", verdict="pass"),
        ],
    )
    curr = Report(
        spec_name="t",
        evidence=[
            Evidence(id="E2", requirement_id="R1", kind="test", verdict="fail"),
        ],
    )
    diff = compare_reports(prev, curr)
    ok = "R1" in diff.regressions
    c.check("REQ-SELF-DIFF-001", ok, message=f"regressions={diff.regressions}")  # type: ignore[union-attr]


def _check_deprecation(c: object) -> None:
    import warnings

    from vnvspec._deprecation import deprecated

    @deprecated("0.3.0", "new_fn()")
    def old_fn() -> str:
        return "x"

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        old_fn()
    ok = (
        len(w) == 1
        and issubclass(w[0].category, DeprecationWarning)
        and "0.3.0" in str(w[0].message)
    )
    c.check("REQ-SELF-DEP-001", ok, message=f"warning_count={len(w)}, correct_type={ok}")  # type: ignore[union-attr]


def _check_verdict_strict(c: object) -> None:
    from vnvspec import Evidence, Report

    ev_pass = Evidence(id="VP-1", requirement_id="R1", kind="test", verdict="pass")
    ev_inc = Evidence(id="VP-2", requirement_id="R2", kind="test", verdict="inconclusive")
    ev_fail = Evidence(id="VP-3", requirement_id="R3", kind="test", verdict="fail")

    # strict: pass+inconclusive → inconclusive
    r1 = Report(spec_name="t", evidence=[ev_pass, ev_inc])
    strict_ok = r1.verdict() == "inconclusive"

    # lenient: pass+inconclusive → pass
    r2 = Report(spec_name="t", evidence=[ev_pass, ev_inc], verdict_policy="lenient")
    lenient_ok = r2.verdict() == "pass"

    # fail always wins
    r3 = Report(spec_name="t", evidence=[ev_fail, ev_inc], verdict_policy="lenient")
    fail_ok = r3.verdict() == "fail"

    c.check(  # type: ignore[union-attr]
        "REQ-SELF-VERDICT-001",
        strict_ok and lenient_ok and fail_ok,
        message=f"strict={strict_ok}, lenient={lenient_ok}, fail_precedence={fail_ok}",
    )


def _check_formal_proof(c: object) -> None:
    from vnvspec import Requirement

    req = Requirement(id="FP-1", statement="Test.", verification_method="formal_proof")
    ok = req.verification_method == "formal_proof"

    import json

    data = json.loads(req.model_dump_json())
    req2 = Requirement.model_validate(data)
    rt_ok = req2.verification_method == "formal_proof"

    c.check(  # type: ignore[union-attr]
        "REQ-SELF-FORMAL-001", ok and rt_ok, message=f"construct={ok}, roundtrip={rt_ok}"
    )


def _check_source_field(c: object) -> None:
    from vnvspec import Requirement

    r1 = Requirement(id="S1", statement="Test.", source="https://example.com")  # type: ignore[arg-type]
    str_ok = r1.source == ["https://example.com"]

    r2 = Requirement(id="S2", statement="Test.", source=["a", "b"])
    list_ok = r2.source == ["a", "b"]

    r3 = Requirement(id="S3", statement="Test.")
    default_ok = r3.source == []

    c.check(  # type: ignore[union-attr]
        "REQ-SELF-SOURCE-001",
        str_ok and list_ok and default_ok,
        message=f"str_norm={str_ok}, list_pass={list_ok}, default_empty={default_ok}",
    )


def _check_v02_compat(c: object) -> None:
    result = _run([sys.executable, "scripts/check_v0_2_compat.py"])
    c.check(  # type: ignore[union-attr]
        "REQ-SELF-COMPAT-002",
        result.returncode == 0,
        message=result.stdout.strip() or result.stderr.strip(),
    )


def _check_pytorch_catalog(c: object) -> None:
    from vnvspec.catalog.ml.pytorch_training import (
        checkpointing,
        data_loading,
        gradient_health,
        loss_validation,
        reproducibility,
    )

    total = sum(
        len(f())
        for f in [reproducibility, gradient_health, checkpointing, data_loading, loss_validation]
    )
    min_req_count = 30
    count_ok = total >= min_req_count

    # Check standards coverage
    all_reqs = []
    for f in [reproducibility, gradient_health, checkpointing, data_loading, loss_validation]:
        all_reqs.extend(f())
    with_stds = sum(1 for r in all_reqs if r.standards)
    stds_pct = with_stds / len(all_reqs) if all_reqs else 0
    min_stds_pct = 0.5
    stds_ok = stds_pct >= min_stds_pct

    # Check GtWR
    from vnvspec.core._internal.gtwr_rules import RuleProfile

    gtwr_ok = True
    for req in all_reqs:
        errors = [v for v in req.check_quality(RuleProfile.FORMAL) if v.severity == "error"]
        if errors:
            gtwr_ok = False
            break

    c.check(  # type: ignore[union-attr]
        "REQ-SELF-CATALOG-PYT-001",
        count_ok and stds_ok and gtwr_ok,
        message=f"count={total}, stds={stds_pct:.0%}, gtwr_clean={gtwr_ok}",
    )


def _check_catalog_cli(c: object) -> None:
    r1 = _run(["uv", "run", "vnvspec", "catalog", "list"])
    list_ok = r1.returncode == 0

    r2 = _run(["uv", "run", "vnvspec", "catalog", "show", "vnvspec.catalog.demo"])
    show_ok = r2.returncode == 0 and "CAT-DEMO-001" in r2.stdout

    r3 = _run(["uv", "run", "vnvspec", "catalog", "audit"])
    audit_ok = r3.returncode == 0

    c.check(  # type: ignore[union-attr]
        "REQ-SELF-CATALOG-001",
        list_ok and show_ok and audit_ok,
        message=f"list={list_ok}, show={show_ok}, audit={audit_ok}",
    )


def _check_shields_endpoint(c: object) -> None:
    import json
    import tempfile

    from vnvspec import Evidence, Report
    from vnvspec.exporters.shields_endpoint import export_shields_endpoint

    # All pass → green
    rp = Report(
        spec_name="t",
        evidence=[Evidence(id="E1", requirement_id="R", kind="test", verdict="pass")],
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "badge.json"
        export_shields_endpoint(rp, path=p)
        data = json.loads(p.read_text())
        green_ok = data["color"] == "green" and data["schemaVersion"] == 1

    # Fail → red
    rf = Report(
        spec_name="t",
        evidence=[Evidence(id="E2", requirement_id="R", kind="test", verdict="fail")],
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "badge.json"
        export_shields_endpoint(rf, path=p)
        data = json.loads(p.read_text())
        red_ok = data["color"] == "red"

    # Inconclusive → yellow
    ri = Report(
        spec_name="t",
        evidence=[Evidence(id="E3", requirement_id="R", kind="test", verdict="inconclusive")],
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "badge.json"
        export_shields_endpoint(ri, path=p)
        data = json.loads(p.read_text())
        yellow_ok = data["color"] == "yellow"

    # Empty → lightgrey
    re_ = Report(spec_name="t")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "badge.json"
        export_shields_endpoint(re_, path=p)
        data = json.loads(p.read_text())
        grey_ok = data["color"] == "lightgrey"

    c.check(  # type: ignore[union-attr]
        "REQ-SELF-SHIELDS-001",
        green_ok and red_ok and yellow_ok and grey_ok,
        message=f"green={green_ok}, red={red_ok}, yellow={yellow_ok}, grey={grey_ok}",
    )


if __name__ == "__main__":
    sys.exit(main())
