"""Catalog infrastructure — discovery, compatibility checking, and utilities.

This module provides the machinery behind ``vnvspec catalog list``,
``vnvspec catalog show``, and ``vnvspec catalog audit``.
"""

from __future__ import annotations

import importlib
import pkgutil
import re
from dataclasses import dataclass, field
from datetime import date
from importlib.metadata import version as get_version
from types import ModuleType
from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from vnvspec.core.requirement import Requirement

CompatibilityLevel = Literal["compatible", "unknown", "incompatible"]


@dataclass(frozen=True)
class CatalogInfo:
    """Metadata about a discovered catalog module."""

    module_path: str
    compatible_with: str
    doc: str
    requirement_count: int


@dataclass(frozen=True)
class CompatibilityReport:
    """Result of checking a catalog module's version pin against installed packages."""

    module_path: str
    compatible_with: str
    level: CompatibilityLevel
    installed_version: str | None = None
    message: str = ""


@dataclass
class AuditResult:
    """Result of auditing all catalog modules."""

    reports: list[CompatibilityReport] = field(default_factory=list)
    stale_modules: list[str] = field(default_factory=list)
    broken_sources: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True if no incompatible modules and no broken sources."""
        return all(r.level != "incompatible" for r in self.reports) and not self.broken_sources


def discover_catalogs() -> list[CatalogInfo]:
    """Discover all catalog modules under ``vnvspec.catalog``.

    Walks the ``vnvspec.catalog`` namespace and finds modules that define
    ``__compatible_with__``. The demo module is included even without a
    compatibility pin.
    """
    import vnvspec.catalog as catalog_pkg  # noqa: PLC0415

    results: list[CatalogInfo] = []
    _walk_catalog_package(catalog_pkg, results)
    return sorted(results, key=lambda c: c.module_path)


def _walk_catalog_package(package: ModuleType, results: list[CatalogInfo]) -> None:
    """Recursively walk a package and collect catalog info."""
    prefix = package.__name__ + "."
    path = package.__path__

    for _importer, modname, _ispkg in pkgutil.walk_packages(path, prefix=prefix):
        if modname.endswith("._base") or modname.endswith(".__init__"):
            continue
        try:
            mod = importlib.import_module(modname)
        except Exception:
            continue

        compat = getattr(mod, "__compatible_with__", "")
        reqs = all_requirements(mod)

        if reqs or compat:
            results.append(
                CatalogInfo(
                    module_path=modname,
                    compatible_with=compat,
                    doc=(mod.__doc__ or "").strip().split("\n")[0],
                    requirement_count=len(reqs),
                )
            )


def all_requirements(module: ModuleType) -> list[Requirement]:
    """Collect all requirements from a catalog module.

    Calls every public callable that returns ``list[Requirement]``.
    """
    results: list[Requirement] = []
    for name in dir(module):
        if name.startswith("_"):
            continue
        obj = getattr(module, name)
        if callable(obj):
            try:
                val = obj()
                if isinstance(val, list) and all(isinstance(r, Requirement) for r in val):
                    results.extend(val)
            except Exception:
                continue
    return results


def check_compatibility(catalog_info: CatalogInfo) -> CompatibilityReport:
    """Check whether the installed package matches the catalog's version pin.

    Uses ``packaging.specifiers`` to evaluate the ``__compatible_with__`` pin
    against the installed package version.
    """
    if not catalog_info.compatible_with:
        return CompatibilityReport(
            module_path=catalog_info.module_path,
            compatible_with="",
            level="unknown",
            message="No version pin declared",
        )

    spec_str = catalog_info.compatible_with
    # Extract package name from specifier like "torch>=2.3,<3.0"
    pkg_name = ""
    for ch in spec_str:
        if ch in ">=<!, ":
            break
        pkg_name += ch

    if not pkg_name:
        return CompatibilityReport(
            module_path=catalog_info.module_path,
            compatible_with=spec_str,
            level="unknown",
            message="Could not parse package name from version pin",
        )

    # Try to find installed version
    try:
        installed = get_version(pkg_name)
    except Exception:
        return CompatibilityReport(
            module_path=catalog_info.module_path,
            compatible_with=spec_str,
            level="unknown",
            installed_version=None,
            message=f"{pkg_name} not installed",
        )

    # Check version against specifier
    version_spec = spec_str[len(pkg_name) :]
    try:
        specifier = SpecifierSet(version_spec)
        is_compatible = Version(installed) in specifier
    except Exception as e:
        return CompatibilityReport(
            module_path=catalog_info.module_path,
            compatible_with=spec_str,
            level="unknown",
            installed_version=installed,
            message=f"Could not evaluate specifier: {e}",
        )

    if is_compatible:
        return CompatibilityReport(
            module_path=catalog_info.module_path,
            compatible_with=spec_str,
            level="compatible",
            installed_version=installed,
            message=f"{pkg_name} {installed} matches {spec_str}",
        )
    return CompatibilityReport(
        module_path=catalog_info.module_path,
        compatible_with=spec_str,
        level="incompatible",
        installed_version=installed,
        message=f"{pkg_name} {installed} does NOT match {spec_str}",
    )


@dataclass(frozen=True)
class StalenessReport:
    """Result of checking a catalog module's last-reviewed date."""

    module_path: str
    last_reviewed: str | None
    days_since_review: int | None
    level: Literal["fresh", "stale", "expired", "unknown"]
    message: str = ""


def check_staleness(
    catalog_info: CatalogInfo,
    *,
    warn_days: int = 180,
    error_days: int = 365,
) -> StalenessReport:
    """Check if a catalog module's review date is stale.

    Parameters
    ----------
    warn_days:
        Days since review before warning (default: 180 = 6 months).
    error_days:
        Days since review before error (default: 365 = 12 months).
    """
    try:
        mod = importlib.import_module(catalog_info.module_path)
    except Exception:
        return StalenessReport(
            module_path=catalog_info.module_path,
            last_reviewed=None,
            days_since_review=None,
            level="unknown",
            message="Could not import module",
        )

    # Look for "Last reviewed: YYYY-MM-DD" in docstring
    doc = mod.__doc__ or ""
    match = re.search(r"Last reviewed:\s*(\d{4}-\d{2}-\d{2})", doc)
    if not match:
        return StalenessReport(
            module_path=catalog_info.module_path,
            last_reviewed=None,
            days_since_review=None,
            level="unknown",
            message="No 'Last reviewed' date in docstring",
        )

    reviewed_str = match.group(1)
    try:
        reviewed_date = date.fromisoformat(reviewed_str)
    except ValueError:
        return StalenessReport(
            module_path=catalog_info.module_path,
            last_reviewed=reviewed_str,
            days_since_review=None,
            level="unknown",
            message=f"Could not parse date: {reviewed_str}",
        )

    days = (date.today() - reviewed_date).days
    if days > error_days:
        level: Literal["fresh", "stale", "expired", "unknown"] = "expired"
    elif days > warn_days:
        level = "stale"
    else:
        level = "fresh"

    return StalenessReport(
        module_path=catalog_info.module_path,
        last_reviewed=reviewed_str,
        days_since_review=days,
        level=level,
        message=f"Reviewed {days} days ago ({reviewed_str})",
    )


def collect_source_urls(catalog_info: CatalogInfo) -> list[str]:
    """Collect all unique source URLs from a catalog module's requirements."""
    try:
        mod = importlib.import_module(catalog_info.module_path)
    except Exception:
        return []

    urls: list[str] = []
    for req in all_requirements(mod):
        for src in req.source:
            if src.startswith("http://") or src.startswith("https://"):
                if src not in urls:
                    urls.append(src)
    return urls
