"""Tests for catalog infrastructure (_base.py)."""

from __future__ import annotations

from vnvspec.catalog._base import (
    CatalogInfo,
    all_requirements,
    check_compatibility,
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
