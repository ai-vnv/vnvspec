"""INCOSE Guide to Writing Requirements (GtWR) rule checks.

Provides heuristic checks for requirement quality. Each rule is a callable
that takes a :class:`Requirement` and returns a :class:`RuleViolation` or None.

These rules are intentionally heuristic — they catch common problems but
are not a substitute for human review.
"""

from __future__ import annotations

import enum
import re
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from vnvspec.core.requirement import Requirement

Severity = Literal["error", "warning", "info"]


class RuleProfile(enum.StrEnum):
    """Rule profile presets for different project types."""

    FORMAL = "formal"
    WEB_APP = "web-app"
    EMBEDDED = "embedded"


# Severity overrides per profile. Keys not listed use the rule's default severity.
_PROFILE_OVERRIDES: dict[RuleProfile, dict[str, Severity]] = {
    RuleProfile.FORMAL: {},
    RuleProfile.WEB_APP: {
        "R6": "info",  # Unit-bearing: web apps rarely have physical units
        "R7": "info",  # Complete (shall-language): web apps use different vocabulary
    },
    RuleProfile.EMBEDDED: {
        "R5": "error",  # Feasible: stricter for safety-critical embedded
    },
}


class RuleViolation(BaseModel):
    """A single rule violation found during quality checking.

    Example:
        >>> v = RuleViolation(
        ...     rule="R1", name="Necessary", severity="error", message="No rationale.",
        ... )
        >>> v.rule
        'R1'
    """

    model_config = {"frozen": True}

    rule: str = Field(description="Rule identifier, e.g. R1.")
    name: str = Field(description="Rule name, e.g. Necessary.")
    severity: Severity = Field(description="Error or warning.")
    message: str = Field(description="Human-readable explanation of the violation.")


# --- Weasel words and impossible quantifiers ---

_WEASEL_WORDS = re.compile(
    r"\b(should|may|might|possibly|as appropriate|as needed|if possible"
    r"|adequate|reasonable|normal|typical)\b",
    re.IGNORECASE,
)

_IMPOSSIBLE_QUANTIFIERS = re.compile(
    r"\b(always|never|perfect|perfectly|100%|all cases|every possible)\b",
    re.IGNORECASE,
)

_CONJUNCTION_SPLIT = re.compile(
    r"\b(and/or)\b|(?<!\w/)(?<!\d)\band\b(?!/)|(?<!\w/)\bor\b(?!/)",
    re.IGNORECASE,
)

_NUMERIC_PATTERN = re.compile(r"\b\d+\.?\d*\b")

_UNIT_PATTERN = re.compile(
    r"\b\d+\.?\d*\s*"
    r"(ms|s|sec|seconds?|minutes?|min|hours?|hr|days?|"
    r"Hz|kHz|MHz|GHz|"
    r"m|km|cm|mm|ft|in|miles?|"
    r"kg|g|mg|lb|lbs|"
    r"m/s|km/h|mph|"
    r"°C|°F|K|"
    r"%|percent|"
    r"MB|GB|TB|KB|bytes?|"
    r"px|pixels?|"
    r"dB|W|kW|V|A|"
    r"samples?|images?|epochs?|iterations?|steps?|"
    r"classes|labels|tokens?)\b",
    re.IGNORECASE,
)

_SUBJECT_PATTERN = re.compile(
    r"\b(the system|the model|the classifier|the detector|the module|the component|"
    r"the service|the API|the interface|the function|the network|it)\b",
    re.IGNORECASE,
)

_SHALL_PATTERN = re.compile(r"\bshall\b", re.IGNORECASE)


def _r1_necessary(req: Requirement) -> RuleViolation | None:
    """R1 Necessary — rationale must be non-empty.

    A requirement without a rationale cannot be judged as necessary.
    """
    if not req.rationale.strip():
        return RuleViolation(
            rule="R1",
            name="Necessary",
            severity="error",
            message="Requirement has no rationale. Explain why this requirement exists.",
        )
    return None


def _r2_singular(req: Requirement) -> RuleViolation | None:
    """R2 Singular — statement should not contain top-level conjunctions.

    Requirements with 'and' or 'or' often conflate multiple concerns.
    Heuristic: flag if the statement contains 'and/or', or standalone 'and'/'or'
    not inside a parenthetical or list context.
    """
    # NOTE(vnvspec): This heuristic may flag legitimate uses of 'and'/'or' in
    # enumerated lists like "labels in {cat, dog, and bird}". If this causes
    # false positives, consider a more sophisticated parse.
    matches = _CONJUNCTION_SPLIT.findall(req.statement)
    if matches:
        return RuleViolation(
            rule="R2",
            name="Singular",
            severity="warning",
            message=(
                f"Statement contains conjunction(s): {matches}. "
                "Consider splitting into separate requirements."
            ),
        )
    return None


def _r3_unambiguous(req: Requirement) -> RuleViolation | None:
    """R3 Unambiguous — no weasel words.

    Words like 'should', 'may', 'possibly', 'as appropriate' introduce
    ambiguity and make the requirement unverifiable.
    """
    found = _WEASEL_WORDS.findall(req.statement)
    if found:
        return RuleViolation(
            rule="R3",
            name="Unambiguous",
            severity="error",
            message=(
                f"Statement contains weasel words: {found}. Use 'shall' for mandatory behavior."
            ),
        )
    return None


def _r4_verifiable(req: Requirement) -> RuleViolation | None:
    """R4 Verifiable — verification method set and acceptance criteria non-empty.

    A requirement that cannot be verified is not a requirement.
    """
    if not req.acceptance_criteria:
        return RuleViolation(
            rule="R4",
            name="Verifiable",
            severity="error",
            message="No acceptance criteria defined. Add at least one concrete criterion.",
        )
    return None


def _r5_feasible(req: Requirement) -> RuleViolation | None:
    """R5 Feasible — no impossible quantifiers.

    Words like 'always', 'never', 'perfect' set unachievable expectations.
    """
    found = _IMPOSSIBLE_QUANTIFIERS.findall(req.statement)
    if found:
        return RuleViolation(
            rule="R5",
            name="Feasible",
            severity="warning",
            message=(
                f"Statement contains impossible quantifiers: {found}. "
                "Consider bounded/measurable alternatives."
            ),
        )
    return None


def _r6_unit_bearing(req: Requirement) -> RuleViolation | None:
    """R6 Unit-bearing — numerics should be accompanied by units.

    If the statement mentions a number, it should include a unit to
    avoid ambiguity (e.g., '100' could be ms, seconds, meters, etc.).
    Heuristic: flag numerics not followed by a recognized unit token.
    """
    numerics = _NUMERIC_PATTERN.findall(req.statement)
    if not numerics:
        return None
    units = _UNIT_PATTERN.findall(req.statement)
    if numerics and not units:
        return RuleViolation(
            rule="R6",
            name="Unit-bearing",
            severity="warning",
            message=(
                f"Statement contains numeric(s) {numerics} without recognized units. "
                "Add units to avoid ambiguity."
            ),
        )
    return None


def _r7_complete(req: Requirement) -> RuleViolation | None:
    """R7 Complete — subject and 'shall' present.

    A complete requirement should identify a subject (the system, the model, etc.)
    and use 'shall' language. This is a heuristic check.
    """
    has_subject = bool(_SUBJECT_PATTERN.search(req.statement))
    has_shall = bool(_SHALL_PATTERN.search(req.statement))

    if not has_subject and not has_shall:
        return RuleViolation(
            rule="R7",
            name="Complete",
            severity="error",
            message=(
                "Statement lacks both a subject (e.g., 'The system') and 'shall' language. "
                "A complete requirement identifies who/what and uses 'shall'."
            ),
        )
    if not has_subject:
        return RuleViolation(
            rule="R7",
            name="Complete",
            severity="warning",
            message="Statement lacks a clear subject (e.g., 'The system shall ...').",
        )
    if not has_shall:
        return RuleViolation(
            rule="R7",
            name="Complete",
            severity="warning",
            message="Statement does not use 'shall' language.",
        )
    return None


def _r8_consistent_id(req: Requirement) -> RuleViolation | None:
    """R8 Consistent — id follows a recognizable pattern.

    IDs should follow a consistent pattern like REQ-NNN or similar.
    This is a basic check; cross-requirement consistency is checked at Spec level.
    """
    if not re.match(r"^[A-Z]+-\w+", req.id):
        return RuleViolation(
            rule="R8",
            name="Consistent",
            severity="warning",
            message=(
                f"ID '{req.id}' does not follow the expected pattern (e.g., REQ-001). "
                "Use a consistent PREFIX-NUMBER format."
            ),
        )
    return None


_ALL_RULES = [
    _r1_necessary,
    _r2_singular,
    _r3_unambiguous,
    _r4_verifiable,
    _r5_feasible,
    _r6_unit_bearing,
    _r7_complete,
    _r8_consistent_id,
]


def check_all(
    req: Requirement,
    *,
    profile: RuleProfile = RuleProfile.FORMAL,
) -> list[RuleViolation]:
    """Run all GtWR rules against a requirement.

    Returns a list of violations (empty if all rules pass).
    The *profile* parameter adjusts severity levels for different
    project types (e.g. "web-app" demotes R6 and R7 to "info").

    Example:
        >>> from vnvspec.core.requirement import Requirement
        >>> r = Requirement(
        ...     id="REQ-001",
        ...     statement="The system shall respond within 100 ms.",
        ...     rationale="Latency budget.",
        ...     verification_method="test",
        ...     acceptance_criteria=["p99 < 100 ms"],
        ... )
        >>> check_all(r)
        []
    """
    overrides = _PROFILE_OVERRIDES.get(profile, {})
    violations: list[RuleViolation] = []
    for rule_fn in _ALL_RULES:
        violation = rule_fn(req)
        if violation is not None:
            # Apply profile severity override
            rule_id = violation.rule
            if rule_id in overrides:
                violation = violation.model_copy(update={"severity": overrides[rule_id]})
            violations.append(violation)
    return violations
