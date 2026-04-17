# Evidence and Assessment

The `Evidence` and assessment models (`AssessmentContext`, `Report`) form the verification output layer of vnvspec. Evidence records what was tested and the outcome; reports aggregate evidence into an overall verdict.

## Evidence

An `Evidence` object records the outcome of a single verification activity.

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | Unique identifier, e.g. `"EV-001"` |
| `requirement_id` | `str` | The requirement this evidence covers |
| `kind` | `EvidenceKind` | One of `"test"`, `"analysis"`, `"inspection"`, `"demonstration"`, `"simulation"` |
| `verdict` | `Verdict` | One of `"pass"`, `"fail"`, `"inconclusive"` |
| `artifact_uri` | `str` | URI or path to the evidence artifact |
| `observed_at` | `datetime` | When the evidence was collected |
| `details` | `dict[str, Any]` | Additional details |

```python
from vnvspec import Evidence

ev = Evidence(
    id="EV-001",
    requirement_id="REQ-001",
    kind="test",
    verdict="pass",
)
```

## AssessmentContext

`AssessmentContext` carries mutable state during an assessment run. It holds a `run_id` and a `metadata` dict that adapters can populate as they execute verification activities.

## Report

A `Report` aggregates evidence from an assessment into a single document.

| Field | Type | Description |
|-------|------|-------------|
| `spec_name` | `str` | Name of the assessed spec |
| `spec_version` | `str` | Spec version |
| `evidence` | `list[Evidence]` | All collected evidence |
| `summary` | `dict[str, Any]` | Summary statistics |

Key methods:

- **`pass_count()`** -- number of evidence items with `"pass"` verdict
- **`fail_count()`** -- number of evidence items with `"fail"` verdict
- **`verdict()`** -- overall verdict: `"pass"` if no fails, `"fail"` if any fail, `"inconclusive"` if no evidence

```python
from vnvspec.core.assessment import Report

report = Report(spec_name="my-spec", spec_version="1.0", evidence=[ev])
print(report.verdict())  # "pass"
```

## Traceability

Use `Spec.evidence_for(requirement_id)` and `Spec.coverage_summary()` to check which requirements have evidence and which are uncovered. The `TraceLink` and `build_trace_graph()` utilities build a full traceability graph using NetworkX.

**API reference:** `vnvspec.core.evidence.Evidence`, `vnvspec.core.assessment.Report`, `vnvspec.core.assessment.AssessmentContext`
