"""Tests for INCOSE GtWR rule checker.

Each rule has at least one pass case and one fail case.
"""

from __future__ import annotations

from vnvspec.core._internal.gtwr_rules import RuleProfile, RuleViolation, check_all
from vnvspec.core.requirement import Requirement


def _good_req(**overrides: object) -> Requirement:
    """Create a textbook-good requirement with optional overrides."""
    defaults: dict[str, object] = {
        "id": "REQ-001",
        "statement": "The system shall classify images with accuracy above 90 percent.",
        "rationale": "High accuracy is needed for safety-critical deployment.",
        "verification_method": "test",
        "acceptance_criteria": ["Accuracy > 90 percent on the held-out test set."],
    }
    defaults.update(overrides)
    return Requirement.model_validate(defaults)


def _bad_req(**overrides: object) -> Requirement:
    """Create a textbook-bad requirement with optional overrides."""
    defaults: dict[str, object] = {
        "id": "bad-id",
        "statement": "The system should probably work fast and safely",
        "rationale": "",
        "verification_method": "test",
        "acceptance_criteria": [],
    }
    defaults.update(overrides)
    return Requirement.model_validate(defaults)


# --- R1 Necessary (rationale non-empty) ---


class TestR1Necessary:
    def test_pass_has_rationale(self) -> None:
        violations = check_all(_good_req())
        r1_violations = [v for v in violations if v.rule == "R1"]
        assert len(r1_violations) == 0

    def test_fail_no_rationale(self) -> None:
        req = _good_req(rationale="")
        violations = check_all(req)
        r1_violations = [v for v in violations if v.rule == "R1"]
        assert len(r1_violations) == 1
        assert r1_violations[0].severity == "error"


# --- R2 Singular (no top-level conjunctions) ---


class TestR2Singular:
    def test_pass_no_conjunction(self) -> None:
        violations = check_all(_good_req())
        r2_violations = [v for v in violations if v.rule == "R2"]
        assert len(r2_violations) == 0

    def test_fail_has_and(self) -> None:
        req = _good_req(statement="The system shall be fast and accurate.")
        violations = check_all(req)
        r2_violations = [v for v in violations if v.rule == "R2"]
        assert len(r2_violations) == 1

    def test_fail_has_and_or(self) -> None:
        req = _good_req(statement="The system shall be fast and/or accurate.")
        violations = check_all(req)
        r2_violations = [v for v in violations if v.rule == "R2"]
        assert len(r2_violations) == 1


# --- R3 Unambiguous (no weasel words) ---


class TestR3Unambiguous:
    def test_pass_no_weasel_words(self) -> None:
        violations = check_all(_good_req())
        r3_violations = [v for v in violations if v.rule == "R3"]
        assert len(r3_violations) == 0

    def test_fail_should(self) -> None:
        req = _good_req(statement="The system should classify images.")
        violations = check_all(req)
        r3_violations = [v for v in violations if v.rule == "R3"]
        assert len(r3_violations) == 1
        assert r3_violations[0].severity == "error"

    def test_fail_may(self) -> None:
        req = _good_req(statement="The system may respond slowly.")
        violations = check_all(req)
        r3_violations = [v for v in violations if v.rule == "R3"]
        assert len(r3_violations) == 1


# --- R4 Verifiable (acceptance criteria non-empty) ---


class TestR4Verifiable:
    def test_pass_has_criteria(self) -> None:
        violations = check_all(_good_req())
        r4_violations = [v for v in violations if v.rule == "R4"]
        assert len(r4_violations) == 0

    def test_fail_no_criteria(self) -> None:
        req = _good_req(acceptance_criteria=[])
        violations = check_all(req)
        r4_violations = [v for v in violations if v.rule == "R4"]
        assert len(r4_violations) == 1


# --- R5 Feasible (no impossible quantifiers) ---


class TestR5Feasible:
    def test_pass_no_impossible(self) -> None:
        violations = check_all(_good_req())
        r5_violations = [v for v in violations if v.rule == "R5"]
        assert len(r5_violations) == 0

    def test_fail_always(self) -> None:
        req = _good_req(statement="The system shall always produce correct output.")
        violations = check_all(req)
        r5_violations = [v for v in violations if v.rule == "R5"]
        assert len(r5_violations) == 1

    def test_fail_never(self) -> None:
        req = _good_req(statement="The system shall never fail.")
        violations = check_all(req)
        r5_violations = [v for v in violations if v.rule == "R5"]
        assert len(r5_violations) == 1

    def test_fail_perfect(self) -> None:
        req = _good_req(statement="The system shall achieve perfect accuracy.")
        violations = check_all(req)
        r5_violations = [v for v in violations if v.rule == "R5"]
        assert len(r5_violations) == 1


# --- R6 Unit-bearing (numerics with units) ---


class TestR6UnitBearing:
    def test_pass_no_numerics(self) -> None:
        violations = check_all(_good_req())
        r6_violations = [v for v in violations if v.rule == "R6"]
        assert len(r6_violations) == 0

    def test_pass_numeric_with_unit(self) -> None:
        req = _good_req(statement="The system shall respond within 100 ms.")
        violations = check_all(req)
        r6_violations = [v for v in violations if v.rule == "R6"]
        assert len(r6_violations) == 0

    def test_fail_numeric_without_unit(self) -> None:
        req = _good_req(statement="The system shall handle 500 requests.")
        violations = check_all(req)
        r6_violations = [v for v in violations if v.rule == "R6"]
        assert len(r6_violations) == 1


# --- R7 Complete (subject + shall) ---


class TestR7Complete:
    def test_pass_complete(self) -> None:
        violations = check_all(_good_req())
        r7_violations = [v for v in violations if v.rule == "R7"]
        assert len(r7_violations) == 0

    def test_fail_no_subject_no_shall(self) -> None:
        req = _good_req(statement="Classify images accurately.")
        violations = check_all(req)
        r7_violations = [v for v in violations if v.rule == "R7"]
        assert len(r7_violations) == 1
        assert r7_violations[0].severity == "error"

    def test_fail_no_subject(self) -> None:
        req = _good_req(statement="Shall classify images.")
        violations = check_all(req)
        r7_violations = [v for v in violations if v.rule == "R7"]
        assert len(r7_violations) == 1
        assert r7_violations[0].severity == "warning"

    def test_fail_no_shall(self) -> None:
        req = _good_req(statement="The system classifies images.")
        violations = check_all(req)
        r7_violations = [v for v in violations if v.rule == "R7"]
        assert len(r7_violations) == 1
        assert r7_violations[0].severity == "warning"


# --- R8 Consistent ID ---


class TestR8ConsistentId:
    def test_pass_good_id(self) -> None:
        violations = check_all(_good_req())
        r8_violations = [v for v in violations if v.rule == "R8"]
        assert len(r8_violations) == 0

    def test_fail_bad_id(self) -> None:
        req = _good_req(id="bad-id")
        violations = check_all(req)
        r8_violations = [v for v in violations if v.rule == "R8"]
        assert len(r8_violations) == 1


# --- Integration ---


class TestIntegration:
    def test_good_requirement_zero_violations(self) -> None:
        violations = check_all(_good_req())
        assert len(violations) == 0

    def test_bad_requirement_multiple_violations(self) -> None:
        violations = check_all(_bad_req())
        min_expected = 3
        assert len(violations) >= min_expected

    def test_check_quality_method(self) -> None:
        req = _bad_req()
        violations = req.check_quality()
        min_expected = 3
        assert len(violations) >= min_expected

    def test_rule_violation_model(self) -> None:
        v = RuleViolation(
            rule="R1",
            name="Necessary",
            severity="error",
            message="Test message.",
        )
        assert v.rule == "R1"
        assert v.name == "Necessary"


# --- Rule profiles ---


class TestRuleProfiles:
    def test_formal_is_default(self) -> None:
        """Formal profile produces the same results as no profile."""
        req = _good_req(statement="The system shall handle 500 requests.")
        v_default = check_all(req)
        v_formal = check_all(req, profile=RuleProfile.FORMAL)
        assert len(v_default) == len(v_formal)

    def test_web_app_demotes_r6(self) -> None:
        """web-app profile demotes R6 (unit-bearing) to info."""
        req = _good_req(statement="The system shall handle 500 requests.")
        formal_v = check_all(req, profile=RuleProfile.FORMAL)
        webapp_v = check_all(req, profile=RuleProfile.WEB_APP)
        r6_formal = [v for v in formal_v if v.rule == "R6"]
        r6_webapp = [v for v in webapp_v if v.rule == "R6"]
        assert len(r6_formal) == 1
        assert r6_formal[0].severity == "warning"
        assert len(r6_webapp) == 1
        assert r6_webapp[0].severity == "info"

    def test_web_app_demotes_r7(self) -> None:
        """web-app profile demotes R7 (shall-language) to info."""
        req = _good_req(statement="The service returns a 200 status code.")
        webapp_v = check_all(req, profile=RuleProfile.WEB_APP)
        r7_webapp = [v for v in webapp_v if v.rule == "R7"]
        assert len(r7_webapp) == 1
        assert r7_webapp[0].severity == "info"

    def test_embedded_promotes_r5(self) -> None:
        """embedded profile promotes R5 (feasible) to error."""
        req = _good_req(statement="The system shall always produce correct output.")
        embedded_v = check_all(req, profile=RuleProfile.EMBEDDED)
        r5_embedded = [v for v in embedded_v if v.rule == "R5"]
        assert len(r5_embedded) == 1
        assert r5_embedded[0].severity == "error"

    def test_web_app_reduces_violations(self) -> None:
        """web-app profile reduces error-level violations vs formal."""
        req = _good_req(statement="The endpoint returns JSON with 200 status code.")
        formal_errors = [
            v for v in check_all(req, profile=RuleProfile.FORMAL) if v.severity == "error"
        ]
        webapp_errors = [
            v for v in check_all(req, profile=RuleProfile.WEB_APP) if v.severity == "error"
        ]
        assert len(webapp_errors) <= len(formal_errors)

    def test_check_quality_with_profile(self) -> None:
        """check_quality method accepts profile parameter."""
        req = _good_req(statement="The system shall handle 500 requests.")
        v_formal = req.check_quality(profile=RuleProfile.FORMAL)
        v_webapp = req.check_quality(profile=RuleProfile.WEB_APP)
        r6_formal = [v for v in v_formal if v.rule == "R6"]
        r6_webapp = [v for v in v_webapp if v.rule == "R6"]
        assert r6_formal[0].severity == "warning"
        assert r6_webapp[0].severity == "info"
