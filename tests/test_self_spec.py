"""Self-spec verification tests.

These tests verify vnvspec against its own self-spec at .vnvspec/self-spec.yaml.
They are marked with @pytest.mark.vnvspec so the pytest-vnvspec plugin captures
evidence when run with --vnvspec-spec=.vnvspec/self-spec.yaml.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from vnvspec import Evidence, Hazard, IOContract, ODD, Requirement, Spec, TraceLink
from vnvspec.cli.main import ExitCode


ROOT = Path(__file__).resolve().parent.parent


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


class TestBackwardCompat:
    @pytest.mark.vnvspec("REQ-SELF-COMPAT-001")
    def test_v01_symbols_importable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_v0_1_compat.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr


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
        assert len(spec.requirements) >= 19

    @pytest.mark.vnvspec("REQ-SELF-META-001")
    def test_self_spec_ids_unique(self) -> None:
        spec = Spec.from_yaml(ROOT / ".vnvspec" / "self-spec.yaml")
        ids = [r.id for r in spec.requirements]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {ids}"

    @pytest.mark.vnvspec("REQ-SELF-META-001")
    def test_self_spec_ids_follow_pattern(self) -> None:
        import re

        spec = Spec.from_yaml(ROOT / ".vnvspec" / "self-spec.yaml")
        for req in spec.requirements:
            assert re.match(r"^[A-Z]+-", req.id), f"{req.id} doesn't match PREFIX-NNN"
