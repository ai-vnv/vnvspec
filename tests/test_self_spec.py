"""Self-spec verification tests.

These tests verify vnvspec against its own self-spec at .vnvspec/self-spec.yaml.
They are marked with @pytest.mark.vnvspec so the pytest-vnvspec plugin captures
evidence when run with --vnvspec-spec=.vnvspec/self-spec.yaml.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from vnvspec import (
    Evidence,
    Hazard,
    IOContract,
    ODD,
    Requirement,
    Spec,
    TraceLink,
    build_trace_graph,
)
from vnvspec.cli.main import ExitCode
from vnvspec.core.errors import (
    AssessmentError,
    ContractError,
    RequirementError,
    SpecError,
    VnvspecError,
)

ROOT = Path(__file__).resolve().parent.parent


# ==========================================================================
# v0.1.0 requirements
# ==========================================================================


class TestFrozenModels:
    @pytest.mark.vnvspec("REQ-SELF-FROZEN-001")
    def test_all_core_models_frozen(self) -> None:
        for cls in [Spec, Requirement, Evidence, Hazard, ODD, IOContract, TraceLink]:
            cfg = getattr(cls, "model_config", {})
            assert cfg.get("frozen", False), f"{cls.__name__} is not frozen"

    @pytest.mark.vnvspec("REQ-SELF-FROZEN-001")
    def test_mutation_raises(self) -> None:
        e = Evidence(id="EV-T", requirement_id="R", kind="test", verdict="pass")
        with pytest.raises(ValidationError):
            e.id = "EV-X"  # type: ignore[misc]


class TestPydanticModels:
    @pytest.mark.vnvspec("REQ-SELF-PYDANTIC-001")
    def test_evidence_round_trip(self) -> None:
        e = Evidence(
            id="EV-1", requirement_id="R-1", kind="test", verdict="pass",
            details={"key": "val"},
        )
        data = json.loads(e.model_dump_json())
        e2 = Evidence.model_validate(data)
        assert e.id == e2.id
        assert e.details == e2.details

    @pytest.mark.vnvspec("REQ-SELF-PYDANTIC-001")
    def test_spec_round_trip(self) -> None:
        req = Requirement(id="R-1", statement="Test.", verification_method="test")
        spec = Spec(name="rt", requirements=[req])
        data = json.loads(spec.model_dump_json())
        spec2 = Spec.model_validate(data)
        assert spec.name == spec2.name
        assert len(spec2.requirements) == 1


class TestSpecValidation:
    @pytest.mark.vnvspec("REQ-SELF-SPEC-001")
    def test_duplicate_req_ids_rejected(self) -> None:
        req = Requirement(id="R-1", statement="X.", verification_method="test")
        with pytest.raises(SpecError, match="Duplicate requirement IDs"):
            Spec(name="bad", requirements=[req, req])

    @pytest.mark.vnvspec("REQ-SELF-SPEC-001")
    def test_duplicate_hazard_ids_rejected(self) -> None:
        h = Hazard(id="H-1", description="X.", severity="S1", exposure="E1",
                   controllability="C1", asil="QM")
        with pytest.raises(SpecError, match="Duplicate hazard IDs"):
            Spec(name="bad", hazards=[h, h])


class TestTraceGraph:
    @pytest.mark.vnvspec("REQ-SELF-TRACE-GRAPH-001")
    def test_cyclic_links_rejected(self) -> None:
        links = [
            TraceLink(source_id="A", target_id="B", relation="derives_from"),
            TraceLink(source_id="B", target_id="A", relation="derives_from"),
        ]
        with pytest.raises(SpecError, match="cycle"):
            build_trace_graph(links)

    @pytest.mark.vnvspec("REQ-SELF-TRACE-GRAPH-001")
    def test_acyclic_links_accepted(self) -> None:
        links = [
            TraceLink(source_id="A", target_id="B", relation="derives_from"),
            TraceLink(source_id="B", target_id="C", relation="verifies"),
        ]
        g = build_trace_graph(links)
        assert len(g.edges) == 2


class TestGtWRRules:
    @pytest.mark.vnvspec("REQ-SELF-GTWR-001")
    def test_good_requirement_zero_violations(self) -> None:
        req = Requirement(
            id="REQ-001",
            statement="The system shall classify images with accuracy above 90 percent.",
            rationale="High accuracy needed.",
            verification_method="test",
            acceptance_criteria=["Accuracy > 90 percent on test set."],
        )
        assert len(req.check_quality()) == 0

    @pytest.mark.vnvspec("REQ-SELF-GTWR-001")
    def test_bad_requirement_multiple_violations(self) -> None:
        req = Requirement(
            id="bad-id",
            statement="The system should probably work fast and safely",
            rationale="",
            verification_method="test",
            acceptance_criteria=[],
        )
        assert len(req.check_quality()) >= 3


class TestRegistries:
    @pytest.mark.vnvspec("REQ-SELF-REGISTRIES-001")
    def test_at_least_5_registries(self) -> None:
        from vnvspec.registries import list_available, load

        names = list_available()
        assert len(names) >= 5
        reg = load("iso_pas_8800")
        assert len(reg.entries) > 0


class TestExporters:
    @pytest.mark.vnvspec("REQ-SELF-EXPORT-001")
    def test_all_export_formats(self) -> None:
        from vnvspec.core.assessment import Report
        from vnvspec.exporters import (
            export_annex_iv,
            export_gsn_mermaid,
            export_html,
            export_json,
            export_markdown,
        )

        report = Report(
            spec_name="test", spec_version="1.0",
            evidence=[Evidence(id="E1", requirement_id="R1", kind="test", verdict="pass")],
        )
        html = export_html(report)
        assert "<html" in html.lower()
        assert '"spec_name"' in export_json(report)
        assert "Verdict" in export_markdown(report)
        assert "flowchart" in export_gsn_mermaid(report).lower()
        assert "Annex IV" in export_annex_iv(report) or "Purpose" in export_annex_iv(report)


class TestErrorHierarchy:
    @pytest.mark.vnvspec("REQ-SELF-ERRORS-001")
    def test_all_errors_inherit_from_vnvspec_error(self) -> None:
        for cls in [SpecError, RequirementError, ContractError, AssessmentError]:
            assert issubclass(cls, VnvspecError)

    @pytest.mark.vnvspec("REQ-SELF-ERRORS-001")
    def test_errors_have_help_url(self) -> None:
        for cls in [SpecError, RequirementError, ContractError, AssessmentError]:
            assert hasattr(cls, "help_url")
            assert cls.help_url.startswith("http")


# ==========================================================================
# v0.2.0 requirements
# ==========================================================================


class TestBackwardCompat:
    @pytest.mark.vnvspec("REQ-SELF-COMPAT-001")
    def test_v01_symbols_importable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_v0_1_compat.py")],
            capture_output=True, text=True, cwd=str(ROOT), check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr


class TestExtendImmutability:
    @pytest.mark.vnvspec("REQ-SELF-FROZEN-002")
    def test_extend_preserves_original(self) -> None:
        req = Requirement(id="R-1", statement="X.", verification_method="test")
        spec = Spec(name="t", requirements=[req])
        new = Requirement(id="R-2", statement="Y.", verification_method="test")
        spec2 = spec.extend([new])
        assert len(spec.requirements) == 1
        assert len(spec2.requirements) == 2


class TestExitCodes:
    @pytest.mark.vnvspec("REQ-SELF-CLI-001")
    def test_exit_code_enum_values(self) -> None:
        assert ExitCode.OK == 0
        assert ExitCode.ASSESSMENT_FAILURES == 1
        assert ExitCode.INCONCLUSIVE == 2
        assert ExitCode.SPEC_VALIDATION_ERROR == 3
        assert ExitCode.USAGE_ERROR == 4
        assert ExitCode.INTERNAL_ERROR == 5


class TestSelfSpecLoadable:
    @pytest.mark.vnvspec("REQ-SELF-META-001")
    def test_self_spec_loads(self) -> None:
        spec = Spec.from_yaml(ROOT / ".vnvspec" / "self-spec.yaml")
        assert spec.name == "vnvspec-self"
        assert len(spec.requirements) >= 26

    @pytest.mark.vnvspec("REQ-SELF-META-001")
    def test_self_spec_ids_unique(self) -> None:
        spec = Spec.from_yaml(ROOT / ".vnvspec" / "self-spec.yaml")
        ids = [r.id for r in spec.requirements]
        assert len(ids) == len(set(ids))

    @pytest.mark.vnvspec("REQ-SELF-META-001")
    def test_self_spec_ids_follow_pattern(self) -> None:
        import re

        spec = Spec.from_yaml(ROOT / ".vnvspec" / "self-spec.yaml")
        for req in spec.requirements:
            assert re.match(r"^[A-Z]+-", req.id), f"{req.id} doesn't match PREFIX-NNN"

    @pytest.mark.vnvspec("REQ-SELF-META-001")
    def test_all_requirements_have_since_metadata(self) -> None:
        spec = Spec.from_yaml(ROOT / ".vnvspec" / "self-spec.yaml")
        for req in spec.requirements:
            assert "since" in req.metadata, f"{req.id} missing metadata.since"
            assert req.metadata["since"] in ("0.1.0", "0.2.0"), (
                f"{req.id} has unexpected since={req.metadata['since']}"
            )
