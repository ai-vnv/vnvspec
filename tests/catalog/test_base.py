"""Tests for catalog infrastructure (_base.py)."""

from __future__ import annotations

from vnvspec.catalog._base import (
    AuditResult,
    CatalogInfo,
    CompatibilityReport,
    all_requirements,
    check_compatibility,
    check_staleness,
    collect_source_urls,
    discover_catalogs,
)


class TestDiscoverCatalogs:
    def test_discovers_demo_module(self) -> None:
        catalogs = discover_catalogs()
        paths = [c.module_path for c in catalogs]
        assert any("demo" in p for p in paths)

    def test_catalog_info_fields(self) -> None:
        catalogs = discover_catalogs()
        demo = next(c for c in catalogs if "demo" in c.module_path)
        assert demo.requirement_count >= 1
        assert demo.doc != ""


class TestAllRequirements:
    def test_demo_module(self) -> None:
        import vnvspec.catalog.demo as demo_mod

        reqs = all_requirements(demo_mod)
        assert len(reqs) >= 1
        assert reqs[0].id == "CAT-DEMO-001"


class TestCheckCompatibility:
    def test_no_version_pin(self) -> None:
        info = CatalogInfo(
            module_path="vnvspec.catalog.demo",
            compatible_with="",
            doc="demo",
            requirement_count=1,
        )
        report = check_compatibility(info)
        assert report.level == "unknown"

    def test_installed_package(self) -> None:
        info = CatalogInfo(
            module_path="test",
            compatible_with="pydantic>=2.0",
            doc="test",
            requirement_count=0,
        )
        report = check_compatibility(info)
        assert report.level == "compatible"

    def test_incompatible_version(self) -> None:
        info = CatalogInfo(
            module_path="test",
            compatible_with="pydantic>=99.0",
            doc="test",
            requirement_count=0,
        )
        report = check_compatibility(info)
        assert report.level == "incompatible"

    def test_uninstalled_package(self) -> None:
        info = CatalogInfo(
            module_path="test",
            compatible_with="nonexistent_pkg>=1.0",
            doc="test",
            requirement_count=0,
        )
        report = check_compatibility(info)
        assert report.level == "unknown"
        assert "not installed" in report.message

    def test_empty_pkg_name(self) -> None:
        info = CatalogInfo(
            module_path="test",
            compatible_with=">=1.0",
            doc="test",
            requirement_count=0,
        )
        report = check_compatibility(info)
        assert report.level == "unknown"
        assert "parse" in report.message.lower()

    def test_bad_specifier(self) -> None:
        info = CatalogInfo(
            module_path="test",
            compatible_with="pydantic[[[invalid",
            doc="test",
            requirement_count=0,
        )
        report = check_compatibility(info)
        assert report.level == "unknown"


class TestCheckStaleness:
    def test_pytorch_catalog_has_review_date(self) -> None:
        info = CatalogInfo(
            module_path="vnvspec.catalog.ml.pytorch_training.reproducibility",
            compatible_with="torch>=2.3,<3.0",
            doc="test",
            requirement_count=6,
        )
        report = check_staleness(info)
        assert report.last_reviewed is not None
        assert report.level in ("fresh", "stale", "expired")

    def test_no_review_date(self) -> None:
        # vnvspec.catalog itself has no "Last reviewed" in its docstring
        info = CatalogInfo(
            module_path="vnvspec.catalog",
            compatible_with="",
            doc="test",
            requirement_count=0,
        )
        report = check_staleness(info)
        assert report.level == "unknown"

    def test_unimportable_module(self) -> None:
        info = CatalogInfo(
            module_path="nonexistent.module.xyz",
            compatible_with="",
            doc="test",
            requirement_count=0,
        )
        report = check_staleness(info)
        assert report.level == "unknown"
        assert "import" in report.message.lower()

    def test_expired_review(self) -> None:
        """Test with a module whose docstring has a very old date."""
        import types

        mod = types.ModuleType("fake_expired")
        mod.__doc__ = "Test.\nLast reviewed: 2020-01-01\n"

        import vnvspec.catalog._base as base

        original_import = base.importlib.import_module

        def mock_import(name: str) -> types.ModuleType:
            if name == "fake_expired":
                return mod
            return original_import(name)

        base.importlib.import_module = mock_import  # type: ignore[assignment]
        try:
            info = CatalogInfo(
                module_path="fake_expired",
                compatible_with="",
                doc="test",
                requirement_count=0,
            )
            report = check_staleness(info)
            assert report.level == "expired"
            assert report.days_since_review is not None
            assert report.days_since_review > 365
        finally:
            base.importlib.import_module = original_import  # type: ignore[assignment]

    def test_stale_review(self) -> None:
        """Test with a date ~8 months ago (stale but not expired)."""
        import types
        from datetime import date, timedelta

        review_date = date.today() - timedelta(days=250)
        mod = types.ModuleType("fake_stale")
        mod.__doc__ = f"Test.\nLast reviewed: {review_date.isoformat()}\n"

        import vnvspec.catalog._base as base

        original_import = base.importlib.import_module

        def mock_import(name: str) -> types.ModuleType:
            if name == "fake_stale":
                return mod
            return original_import(name)

        base.importlib.import_module = mock_import  # type: ignore[assignment]
        try:
            info = CatalogInfo(
                module_path="fake_stale",
                compatible_with="",
                doc="test",
                requirement_count=0,
            )
            report = check_staleness(info)
            assert report.level == "stale"
        finally:
            base.importlib.import_module = original_import  # type: ignore[assignment]


class TestCollectSourceUrls:
    def test_demo_has_urls(self) -> None:
        info = CatalogInfo(
            module_path="vnvspec.catalog.demo",
            compatible_with="",
            doc="test",
            requirement_count=1,
        )
        urls = collect_source_urls(info)
        assert len(urls) >= 1
        assert all(u.startswith("https://") for u in urls)

    def test_unimportable_module_returns_empty(self) -> None:
        info = CatalogInfo(
            module_path="nonexistent.module.xyz",
            compatible_with="",
            doc="test",
            requirement_count=0,
        )
        urls = collect_source_urls(info)
        assert urls == []

    def test_pytorch_has_multiple_urls(self) -> None:
        info = CatalogInfo(
            module_path="vnvspec.catalog.ml.pytorch_training.reproducibility",
            compatible_with="torch>=2.3,<3.0",
            doc="test",
            requirement_count=6,
        )
        urls = collect_source_urls(info)
        assert len(urls) >= 2


class TestAuditResult:
    def test_ok_when_all_compatible(self) -> None:
        result = AuditResult(
            reports=[
                CompatibilityReport(module_path="a", compatible_with="x>=1", level="compatible"),
            ]
        )
        assert result.ok is True

    def test_not_ok_when_incompatible(self) -> None:
        result = AuditResult(
            reports=[
                CompatibilityReport(module_path="a", compatible_with="x>=1", level="incompatible"),
            ]
        )
        assert result.ok is False

    def test_not_ok_when_broken_sources(self) -> None:
        result = AuditResult(broken_sources=["https://broken.example.com"])
        assert result.ok is False
