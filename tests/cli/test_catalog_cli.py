"""Tests for vnvspec catalog and export CLI subcommands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from vnvspec.cli.main import app
from vnvspec.core.assessment import Report
from vnvspec.core.evidence import Evidence

runner = CliRunner()


class TestCatalogList:
    def test_lists_demo(self) -> None:
        result = runner.invoke(app, ["catalog", "list"])
        assert result.exit_code == 0
        assert "catalog.d" in result.stdout  # Rich truncates long module paths


class TestCatalogShow:
    def test_show_demo(self) -> None:
        result = runner.invoke(app, ["catalog", "show", "vnvspec.catalog.demo"])
        assert result.exit_code == 0
        assert "CAT-DEMO-001" in result.stdout

    def test_show_bad_module(self) -> None:
        result = runner.invoke(app, ["catalog", "show", "vnvspec.catalog.nonexistent"])
        assert result.exit_code != 0


class TestCatalogAudit:
    def test_audit_runs(self) -> None:
        result = runner.invoke(app, ["catalog", "audit"])
        assert result.exit_code == 0


class TestCatalogImport:
    def test_import_yaml(self) -> None:
        result = runner.invoke(
            app, ["catalog", "import", "vnvspec.catalog.demo", "--format", "yaml"]
        )
        assert result.exit_code == 0
        assert "CAT-DEMO-001" in result.stdout

    def test_import_json(self) -> None:
        result = runner.invoke(
            app, ["catalog", "import", "vnvspec.catalog.demo", "--format", "json"]
        )
        assert result.exit_code == 0
        assert "CAT-DEMO-001" in result.stdout

    def test_import_bad_module(self) -> None:
        result = runner.invoke(app, ["catalog", "import", "vnvspec.catalog.nonexistent"])
        assert result.exit_code != 0


class TestExportShieldsEndpoint:
    def test_export_shields_endpoint(self, tmp_path: Path) -> None:
        report = Report(
            spec_name="test",
            evidence=[
                Evidence(id="EV-1", requirement_id="R1", kind="test", verdict="pass"),
            ],
        )
        report_path = tmp_path / "report.json"
        report_path.write_text(report.model_dump_json(), encoding="utf-8")
        output_path = tmp_path / "badge.json"
        result = runner.invoke(
            app,
            ["export-shields-endpoint", str(report_path), "-o", str(output_path)],
        )
        assert result.exit_code == 0
        data = json.loads(output_path.read_text())
        assert data["color"] == "green"

    def test_export_shields_bad_path(self) -> None:
        result = runner.invoke(app, ["export-shields-endpoint", "nonexistent.json"])
        assert result.exit_code != 0
