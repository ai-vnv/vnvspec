"""Shared fixtures for catalog tests.

The ``catalog_requirements`` fixture and auto-generated test class
``TestCatalogRequirements`` validate that every shipped catalog requirement
meets the inclusion policy defined in CONTRIBUTING-CATALOG.md.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable

import pytest

from vnvspec.core.requirement import Requirement

# Pattern: CAT-<PKG3>-<TOPIC4>-<NNN>  (3-letter pkg, up to 5-letter topic, 3-digit number)
_CAT_ID_RE = re.compile(r"^CAT-[A-Z]{2,5}-[A-Z]{2,6}-\d{3}$")

_VALID_PRIORITIES = {"blocking", "high", "medium", "low"}


def validate_catalog_requirement(req: Requirement) -> list[str]:
    """Validate a single catalog requirement against the inclusion policy.

    Returns a list of violation messages (empty = passes).
    """
    violations: list[str] = []

    # 1. ID convention
    if not _CAT_ID_RE.match(req.id):
        violations.append(f"{req.id}: ID does not match CAT-<PKG>-<TOPIC>-<NNN> pattern")

    # 2. Source populated
    if not req.source:
        violations.append(f"{req.id}: source field is empty (at least one URL required)")

    # 3. Valid priority
    if req.priority not in _VALID_PRIORITIES:
        violations.append(f"{req.id}: invalid priority '{req.priority}'")

    # 4. GtWR formal profile — zero error-severity violations
    from vnvspec.core._internal.gtwr_rules import RuleProfile

    gtwr_violations = req.check_quality(profile=RuleProfile.FORMAL)
    errors = [v for v in gtwr_violations if v.severity == "error"]
    if errors:
        msgs = "; ".join(f"{v.rule}: {v.message}" for v in errors)
        violations.append(f"{req.id}: GtWR errors: {msgs}")

    # 5. JSON round-trip
    try:
        data = json.loads(req.model_dump_json())
        req2 = Requirement.model_validate(data)
        if req != req2:
            violations.append(f"{req.id}: JSON round-trip produced different object")
    except Exception as e:
        violations.append(f"{req.id}: JSON round-trip failed: {e}")

    # 6. Dict round-trip (covers YAML/TOML since they go through dict)
    try:
        d = req.model_dump()
        req3 = Requirement.model_validate(d)
        if req != req3:
            violations.append(f"{req.id}: dict round-trip produced different object")
    except Exception as e:
        violations.append(f"{req.id}: dict round-trip failed: {e}")

    return violations


CatalogFunction = Callable[[], list[Requirement]]


@pytest.fixture
def catalog_validator() -> Callable[[Requirement], list[str]]:
    """Fixture that returns the validation function for catalog requirements."""
    return validate_catalog_requirement
