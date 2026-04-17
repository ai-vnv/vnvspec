"""Tests for vnvspec CLI validate command — multi-format support."""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from vnvspec.cli.main import ExitCode, app
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec

runner = CliRunner()


@pytest.fixture()
def sample_spec() -> Spec:
    req = Requirement(
        id="REQ-001",
        statement="The system shall produce valid outputs.",
        rationale="Safety.",
        verification_method="test",
        acceptance_criteria=["All outputs are valid."],
    )
    return Spec(name="test-cli", requirements=[req])


class TestValidateMultiFormat:
    @pytest.mark.vnvspec("REQ-SELF-CLI-002")
    def test_validate_yaml(self, sample_spec: Spec, tmp_path: Path) -> None:
        p = tmp_path / "spec.yaml"
        sample_spec.to_yaml(p)
        result = runner.invoke(app, ["validate", str(p)])
        assert result.exit_code in (ExitCode.OK, ExitCode.ASSESSMENT_FAILURES)
        assert "1 requirements" in result.stdout

    @pytest.mark.vnvspec("REQ-SELF-CLI-002")
    def test_validate_yml(self, sample_spec: Spec, tmp_path: Path) -> None:
        p = tmp_path / "spec.yml"
        sample_spec.to_yaml(p)
        result = runner.invoke(app, ["validate", str(p)])
        assert result.exit_code in (ExitCode.OK, ExitCode.ASSESSMENT_FAILURES)
        assert "1 requirements" in result.stdout

    @pytest.mark.vnvspec("REQ-SELF-CLI-002")
    def test_validate_json(self, sample_spec: Spec, tmp_path: Path) -> None:
        p = tmp_path / "spec.json"
        sample_spec.to_json(p)
        result = runner.invoke(app, ["validate", str(p)])
        assert result.exit_code in (ExitCode.OK, ExitCode.ASSESSMENT_FAILURES)
        assert "1 requirements" in result.stdout

    @pytest.mark.vnvspec("REQ-SELF-CLI-002")
    def test_validate_toml(self, sample_spec: Spec, tmp_path: Path) -> None:
        p = tmp_path / "spec.toml"
        sample_spec.to_toml(p)
        result = runner.invoke(app, ["validate", str(p)])
        assert result.exit_code in (ExitCode.OK, ExitCode.ASSESSMENT_FAILURES)
        assert "1 requirements" in result.stdout

    @pytest.mark.vnvspec("REQ-SELF-CLI-002")
    def test_validate_unsupported_ext(self, tmp_path: Path) -> None:
        p = tmp_path / "spec.txt"
        p.write_text("name: x\n")
        result = runner.invoke(app, ["validate", str(p)])
        assert result.exit_code == ExitCode.SPEC_VALIDATION_ERROR
        assert "Unsupported file extension" in result.stdout
