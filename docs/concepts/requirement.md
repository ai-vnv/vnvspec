# Requirement

The `Requirement` class is the atomic unit of a V&V specification. Each requirement captures a single, verifiable statement about expected system behavior, with metadata for traceability and quality checking.

## Purpose

Requirements are the foundation of any V&V specification. vnvspec requirements follow INCOSE "Guide to Writing Requirements" (GtWR) conventions: each statement should use shall-language, be unambiguous, testable, and traceable to standards clauses.

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier, e.g. `"REQ-001"` |
| `statement` | `str` | The requirement in shall-language |
| `rationale` | `str` | Why this requirement exists |
| `priority` | `Priority` | One of `"blocking"`, `"high"`, `"medium"`, `"low"` |
| `verification_method` | `VerificationMethod` | One of `"test"`, `"analysis"`, `"inspection"`, `"demonstration"`, `"simulation"` |
| `standards` | `dict[str, list[str]]` | Mapping of standard name to clause IDs |
| `acceptance_criteria` | `list[str]` | Concrete pass/fail criteria |

## GtWR Quality Checking

The `check_quality()` method runs INCOSE GtWR rule checks against the requirement and returns a list of `RuleViolation` objects. An empty list means the requirement passes all checks.

```python
from vnvspec import Requirement

req = Requirement(
    id="REQ-001",
    statement="The system should work.",
)
violations = req.check_quality()
for v in violations:
    print(f"{v.rule}: {v.message}")
```

Common violations include missing shall-language, vague terms ("should", "may"), missing rationale, and missing acceptance criteria.

## Standards Traceability

The `standards` field lets you link a requirement to specific clauses in safety standards:

```python
req = Requirement(
    id="REQ-002",
    statement="The model shall be robust to domain shift.",
    verification_method="test",
    standards={"iso_pas_8800": ["6.2.1"], "iso_21448": ["5.3"]},
)
```

**API reference:** `vnvspec.core.requirement.Requirement`
