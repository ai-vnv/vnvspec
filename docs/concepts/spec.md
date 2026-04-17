# Spec

The `Spec` class is the top-level container in vnvspec. It aggregates requirements, IO contracts, operational design domains, hazards, and evidence into a single, coherent specification document.

## Purpose

A Spec represents a complete V&V specification for a system or component. It enforces structural integrity (e.g., unique requirement IDs, unique hazard IDs) and provides convenience methods for querying its contents.

## Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Specification name (required) |
| `version` | `str` | Semantic version, defaults to `"0.1.0"` |
| `requirements` | `list[Requirement]` | Verifiable requirements |
| `contracts` | `list[IOContract]` | Input-output contracts |
| `odds` | `list[ODD]` | Operational design domains |
| `hazards` | `list[Hazard]` | Identified hazards |
| `evidence` | `list[Evidence]` | Collected verification evidence |
| `metadata` | `dict[str, Any]` | Arbitrary additional metadata |

## Validation

Spec validates on construction that all requirement IDs and hazard IDs are unique. Duplicate IDs raise a `SpecError`.

## Methods

- **`get_requirement(requirement_id)`** -- look up a requirement by ID; raises `SpecError` if not found.
- **`get_hazard(hazard_id)`** -- look up a hazard by ID; raises `SpecError` if not found.
- **`evidence_for(requirement_id)`** -- return all evidence linked to a given requirement.
- **`coverage_summary()`** -- return a dict with `total`, `covered`, and `uncovered` requirement counts.

## Example

```python
from vnvspec import Requirement, Spec

req = Requirement(
    id="REQ-001",
    statement="The system shall classify images with accuracy above 0.9.",
    rationale="High accuracy is needed for safety-critical deployment.",
    verification_method="test",
    acceptance_criteria=["Accuracy > 0.9 on the test set."],
)

spec = Spec(name="my-system", requirements=[req])
print(spec.coverage_summary())  # {'total': 1, 'covered': 0, 'uncovered': 1}
```

**API reference:** `vnvspec.core.spec.Spec`
