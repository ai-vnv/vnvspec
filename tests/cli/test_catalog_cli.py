"""Tests for vnvspec catalog CLI subcommands."""

from __future__ import annotations

from typer.testing import CliRunner

from vnvspec.cli.main import app

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
