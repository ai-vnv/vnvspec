#!/usr/bin/env python3
"""Generate the three tutorial notebooks as .ipynb files."""

import json
from pathlib import Path

HERE = Path(__file__).parent


def cell(cell_type: str, source: str) -> dict:
    """Create a notebook cell."""
    c: dict = {
        "cell_type": cell_type,
        "metadata": {},
        "source": source.strip().splitlines(keepends=True),
    }
    if cell_type == "code":
        c["outputs"] = []
        c["execution_count"] = None
    return c


def md(source: str) -> dict:
    return cell("markdown", source)


def code(source: str) -> dict:
    return cell("code", source)


def notebook(cells: list[dict]) -> dict:
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0",
            },
        },
        "cells": cells,
    }


def save(nb: dict, name: str) -> None:
    path = HERE / name
    path.write_text(json.dumps(nb, indent=1, ensure_ascii=False))
    print(f"  Created {path}")


# ═══════════════════════════════════════════════════════════════════════════
# NOTEBOOK 1 — Student Introduction
# ═══════════════════════════════════════════════════════════════════════════

def nb_student() -> dict:
    return notebook([
        # --- Title ---
        md("""
# Introduction to Verification & Validation for AI Systems

**Audience:** Students with ML/programming background but no V&V experience.

**What you'll learn:**
1. What V&V means and why it matters for AI
2. How to write *good* requirements (the INCOSE way)
3. How to build a specification, create evidence, and generate reports
4. How to trace everything back to safety standards

**Time:** ~30 minutes

---
"""),

        # --- Setup ---
        md("## 1. Setup"),
        code("""
import sys, os
sys.path.insert(0, os.path.abspath(".."))

# If running from the repo root, use: sys.path.insert(0, ".")
# Install: pip install vnvspec matplotlib

import vnvspec
print(f"vnvspec version: {vnvspec.__version__}")
"""),
        code("""
# Import our visualization helpers (same directory as this notebook)
from _helpers import (
    display_requirements_table,
    display_violations_table,
    display_evidence_table,
    display_report_summary,
    display_requirement_card,
    plot_violations_by_rule,
    plot_evidence_verdicts,
    plot_coverage,
    display_registry_sample,
)
print("Helpers loaded.")
"""),

        # --- What is V&V? ---
        md("""
## 2. What is Verification & Validation?

Think of building a self-driving car's perception system:

| Question | V&V Term | Meaning |
|----------|----------|---------|
| "Are we building it right?" | **Verification** | Does the system meet its *specifications*? |
| "Are we building the right thing?" | **Validation** | Does the system meet the *user's actual needs*? |

**Without V&V**, you might train a model that scores 99% accuracy on a benchmark
but fails catastrophically in fog, at night, or on unusual road signs.

**With V&V**, you write down *exactly* what the system must do (requirements),
*prove* it does those things (evidence), and *trace* everything to safety standards.

Let's see how `vnvspec` makes this concrete.
"""),

        # --- Your first requirement ---
        md("""
## 3. Your First Requirement

A **requirement** is a single, testable statement about what the system *shall* do.

Let's write one:
"""),
        code("""
from vnvspec import Requirement

# A well-written requirement
req_good = Requirement(
    id="REQ-001",
    statement="The classifier shall produce output probabilities in the range [0.0, 1.0].",
    rationale="Downstream calibration requires valid probability outputs.",
    verification_method="test",
    acceptance_criteria=[
        "All output values are between 0.0 and 1.0 inclusive.",
        "Output probabilities sum to 1.0 within tolerance of 0.01.",
    ],
    priority="high",
)

display_requirement_card(req_good)
"""),

        # --- Good vs bad requirements ---
        md("""
## 4. Good vs. Bad Requirements — The GtWR Checker

The **INCOSE Guide to Writing Requirements (GtWR)** defines 8 rules for requirement quality.
vnvspec has a built-in checker. Let's compare a good and a bad requirement:
"""),
        code("""
# Check the good requirement
violations = req_good.check_quality()
print(f"Good requirement violations: {len(violations)}")
display_violations_table(violations)
"""),
        code("""
# Now a BAD requirement — vague, ambiguous, no criteria
req_bad = Requirement(
    id="bad-req",
    statement="The system should probably work fast and safely",
    rationale="",                # no rationale!
    verification_method="test",
    acceptance_criteria=[],      # no criteria!
)

violations_bad = req_bad.check_quality()
print(f"Bad requirement violations: {len(violations_bad)}")
display_violations_table(violations_bad)
"""),
        code("""
# Visualize the violations
plot_violations_by_rule(violations_bad, title="What's wrong with the bad requirement?")
"""),

        md("""
**Key takeaway:** Good requirements are *singular* (one thing), *unambiguous* (no "should" or "maybe"),
*verifiable* (clear pass/fail criteria), and *necessary* (justified by a rationale).
"""),

        # --- Building a spec ---
        md("""
## 5. Building a Specification

A **Spec** groups requirements together with hazards, contracts, and evidence.
Let's create a spec for a simple image classifier:
"""),
        code("""
from vnvspec import Spec, Requirement

# Define 4 requirements
requirements = [
    Requirement(
        id="REQ-PROB",
        statement="The classifier shall produce probabilities in [0.0, 1.0].",
        rationale="Valid probability outputs for calibration.",
        verification_method="test",
        acceptance_criteria=["All outputs in [0.0, 1.0]."],
        priority="high",
    ),
    Requirement(
        id="REQ-DIM",
        statement="The classifier shall output exactly 3 class scores.",
        rationale="The dataset has 3 classes.",
        verification_method="test",
        acceptance_criteria=["Output dimension equals 3."],
    ),
    Requirement(
        id="REQ-NAN",
        statement="The classifier shall not produce NaN values.",
        rationale="NaN propagation causes silent failures.",
        verification_method="test",
        acceptance_criteria=["No NaN in any output tensor."],
        priority="high",
    ),
    Requirement(
        id="REQ-LATENCY",
        statement="The classifier shall produce a prediction within 50 ms per sample.",
        rationale="Real-time inference budget.",
        verification_method="test",
        acceptance_criteria=["p99 latency < 50 ms."],
    ),
]

spec = Spec(name="image-classifier-v1", requirements=requirements)
print(f"Spec '{spec.name}' has {len(spec.requirements)} requirements")
display_requirements_table(spec.requirements)
"""),

        # --- Check quality of all requirements ---
        code("""
# Batch quality check
print("Quality check for all requirements:\\n")
all_violations = []
for req in spec.requirements:
    v = req.check_quality()
    all_violations.extend(v)
    status = "PASS" if not v else f"{len(v)} issues"
    print(f"  {req.id}: {status}")

print(f"\\nTotal violations: {len(all_violations)}")
"""),

        # --- A simple model ---
        md("""
## 6. A Simple "Model"

You don't need PyTorch to understand V&V! Let's use a plain Python function as our "model":
"""),
        code("""
import random
import math

def simple_classifier(features: list[float]) -> list[float]:
    \"\"\"A fake classifier that returns 3 class probabilities.\"\"\"
    # Simulate some logits
    logits = [sum(f * w for f, w in zip(features, [0.3, -0.1, 0.5])) + random.gauss(0, 0.1)
              for _ in range(3)]
    # Softmax
    max_l = max(logits)
    exps = [math.exp(l - max_l) for l in logits]
    total = sum(exps)
    return [e / total for e in exps]

# Test it
sample_input = [0.5, 1.2, -0.3]
output = simple_classifier(sample_input)
print(f"Input:  {sample_input}")
print(f"Output: {[f'{p:.4f}' for p in output]}")
print(f"Sum:    {sum(output):.6f}")
"""),

        # --- Creating evidence ---
        md("""
## 7. Creating Evidence

Now let's *verify* our model against the spec by running it on test data
and recording **Evidence** objects:
"""),
        code("""
from vnvspec import Evidence
from datetime import datetime, UTC
import math

# Generate test data
test_data = [[random.gauss(0, 1) for _ in range(3)] for _ in range(100)]

# Run the model
outputs = [simple_classifier(x) for x in test_data]

# --- REQ-PROB: probabilities in [0, 1]? ---
all_in_range = all(0.0 <= p <= 1.0 for out in outputs for p in out)
ev_prob = Evidence(
    id="EV-PROB-001",
    requirement_id="REQ-PROB",
    kind="test",
    verdict="pass" if all_in_range else "fail",
    details={"samples": len(test_data), "all_in_range": all_in_range},
)

# --- REQ-DIM: output dimension == 3? ---
all_dim3 = all(len(out) == 3 for out in outputs)
ev_dim = Evidence(
    id="EV-DIM-001",
    requirement_id="REQ-DIM",
    kind="test",
    verdict="pass" if all_dim3 else "fail",
    details={"samples": len(test_data)},
)

# --- REQ-NAN: no NaN? ---
has_nan = any(math.isnan(p) for out in outputs for p in out)
ev_nan = Evidence(
    id="EV-NAN-001",
    requirement_id="REQ-NAN",
    kind="test",
    verdict="fail" if has_nan else "pass",
    details={"nan_count": sum(1 for out in outputs for p in out if math.isnan(p))},
)

# --- REQ-LATENCY: not tested yet ---
ev_latency = Evidence(
    id="EV-LAT-001",
    requirement_id="REQ-LATENCY",
    kind="test",
    verdict="inconclusive",
    details={"note": "Latency benchmark not yet run."},
)

evidence = [ev_prob, ev_dim, ev_nan, ev_latency]
display_evidence_table(evidence)
"""),

        # --- Building a report ---
        md("## 8. Building a Report"),
        code("""
from vnvspec.core.assessment import Report

report = Report(
    spec_name=spec.name,
    spec_version=spec.version,
    evidence=evidence,
    summary={"test_samples": 100, "model": "simple_classifier"},
)

display_report_summary(report)
"""),
        code("""
# Visualize verdicts
plot_evidence_verdicts(report.evidence, title="How did our model do?")
"""),

        # --- Coverage ---
        md("## 9. Coverage — Are All Requirements Tested?"),
        code("""
# Add evidence to the spec to check coverage
spec_with_ev = Spec(
    name=spec.name,
    requirements=spec.requirements,
    evidence=evidence,
)

print("Coverage summary:", spec_with_ev.coverage_summary())
plot_coverage(spec_with_ev)
"""),

        # --- Exporting ---
        md("""
## 10. Exporting Your Report

vnvspec can export reports in multiple formats:
"""),
        code("""
from vnvspec.exporters import export_markdown, export_gsn_mermaid

# Markdown report
md_report = export_markdown(report)
print(md_report)
"""),
        code("""
# GSN assurance case (Mermaid diagram)
gsn = export_gsn_mermaid(report)
print(gsn)
"""),
        code("""
from _helpers import display_mermaid
display_mermaid(gsn)
"""),

        # --- Traceability ---
        md("""
## 11. Traceability — Connecting the Dots

Real V&V requires *tracing* requirements to hazards, evidence, and standards.
"""),
        code("""
from vnvspec import TraceLink, Hazard, build_trace_graph
from vnvspec.core.trace import coverage_report
from _helpers import plot_trace_graph

# Define a hazard
haz = Hazard(
    id="HAZ-001",
    description="Incorrect classification leads to wrong action.",
    severity="S3", exposure="E4", controllability="C3", asil="D",
    mitigations=["REQ-PROB", "REQ-NAN"],
)

# Create trace links
links = [
    TraceLink(source_id="REQ-PROB", target_id="HAZ-001", relation="mitigates"),
    TraceLink(source_id="REQ-NAN", target_id="HAZ-001", relation="mitigates"),
    TraceLink(source_id="EV-PROB-001", target_id="REQ-PROB", relation="verifies"),
    TraceLink(source_id="EV-NAN-001", target_id="REQ-NAN", relation="verifies"),
    TraceLink(source_id="EV-DIM-001", target_id="REQ-DIM", relation="verifies"),
    TraceLink(source_id="REQ-PROB", target_id="ISO-8800-6.2", relation="maps_to_standard"),
]

plot_trace_graph(links)
"""),

        # --- Standards ---
        md("""
## 12. Standards Registries

vnvspec ships with clause databases for major safety standards:
"""),
        code("""
from vnvspec.registries import list_available
print("Available registries:", list_available())
"""),
        code("""
display_registry_sample("iso_pas_8800", n=8)
"""),

        # --- Summary ---
        md("""
## Summary

| Concept | What it is | vnvspec class |
|---------|-----------|---------------|
| Requirement | A testable "shall" statement | `Requirement` |
| Specification | Collection of requirements + context | `Spec` |
| Evidence | Proof that a requirement is met | `Evidence` |
| Hazard | An identified risk | `Hazard` |
| Traceability | Links between all artifacts | `TraceLink` |
| Report | Assessment results | `Report` |

**Next steps:**
- Try Notebook 2 (SE perspective) for standards compliance and formal traceability
- Try Notebook 3 (ML perspective) for PyTorch model wrapping and automated assessment
"""),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# NOTEBOOK 2 — SE Professional
# ═══════════════════════════════════════════════════════════════════════════

def nb_se_pro() -> dict:
    return notebook([
        md("""
# V&V for ML Systems: A Systems Engineering Perspective

**Audience:** SE professionals who know requirements engineering, FMEA/HARA, and traceability — but want to see how these apply to ML components.

**What you'll learn:**
1. How traditional V&V concepts map to ML systems
2. Formalizing requirements with INCOSE GtWR quality gates
3. HARA, ODD, and I/O contracts for ML components
4. Standards compliance mapping (ISO/PAS 8800, ISO 21448, EU AI Act)
5. Automated traceability and compliance documentation

**Time:** ~35 minutes

---
"""),

        # --- Setup ---
        md("## 1. Setup"),
        code("""
import sys, os
sys.path.insert(0, os.path.abspath(".."))

from vnvspec import (
    Spec, Requirement, Evidence, Hazard, ODD,
    IOContract, Invariant, TraceLink,
    build_trace_graph, coverage_report,
)
from vnvspec.core.assessment import Report
from vnvspec.registries import load, list_available
from vnvspec.exporters import (
    export_html, export_markdown, export_gsn_mermaid,
    export_annex_iv, export_json,
)
from vnvspec.runners.pytest_gen import generate_pytest
from vnvspec.runners.hypothesis_gen import generate_hypothesis

from _helpers import (
    display_requirements_table, display_violations_table,
    display_evidence_table, display_report_summary,
    plot_violations_by_rule, plot_evidence_verdicts,
    plot_coverage, plot_trace_graph,
    display_registry_sample, display_mermaid,
)
print("All imports ready.")
"""),

        # --- SE concepts mapping ---
        md("""
## 2. Traditional V&V vs. ML V&V

| SE Concept | Traditional | ML Equivalent |
|-----------|------------|---------------|
| **Requirements** | "The brake shall engage within 200 ms" | "The classifier shall produce probabilities in [0, 1]" |
| **Design spec** | Circuit schematic, state machine | Model architecture, hyperparameters, training config |
| **Verification** | Unit test, integration test, static analysis | Model evaluation, property testing, formal invariants |
| **Validation** | Acceptance testing with stakeholders | ODD coverage, scenario-based testing, field trials |
| **HARA** | Hardware FMEA, FTA | ML-specific hazard analysis (data quality, distribution shift, adversarial) |
| **Traceability** | Requirements → tests → code | Requirements → model behavior → evidence → standards |

The key difference: **ML systems have stochastic behavior**. You can't prove correctness — you collect *evidence* and manage *risk*.
"""),

        # --- Formal requirements ---
        md("""
## 3. Formalizing Requirements for an ML Component

Let's spec a perception classifier for an autonomous vehicle:
"""),
        code("""
# A real-ish set of requirements for an AV perception classifier
requirements = [
    Requirement(
        id="REQ-FUNC-001",
        statement="The classifier shall assign exactly one label from the set {vehicle, pedestrian, cyclist, background} to each detected object.",
        rationale="Mutual exclusivity required by the tracking module.",
        verification_method="test",
        acceptance_criteria=["Output argmax yields exactly one label per detection."],
        standards={"iso_pas_8800": ["6.3.1"], "iso_21448": ["5.2"]},
        priority="high",
    ),
    Requirement(
        id="REQ-PERF-001",
        statement="The classifier shall achieve mean average precision above 0.85 on the validation set.",
        rationale="Performance floor derived from SOTIF residual-risk analysis.",
        verification_method="test",
        acceptance_criteria=["mAP >= 0.85 on the held-out validation set."],
        standards={"iso_21448": ["6.3", "10.1"]},
        priority="high",
    ),
    Requirement(
        id="REQ-ROB-001",
        statement="The classifier shall maintain precision above 0.70 under gaussian noise with sigma 0.1.",
        rationale="Sensor noise robustness per ISO/PAS 8800 clause 7.4.",
        verification_method="test",
        acceptance_criteria=["Precision > 0.70 with noise augmentation (sigma=0.1)."],
        standards={"iso_pas_8800": ["7.4"]},
    ),
    Requirement(
        id="REQ-DATA-001",
        statement="The training dataset shall contain at least 1000 samples per class.",
        rationale="Data sufficiency for statistical significance.",
        verification_method="inspection",
        acceptance_criteria=["Dataset class histogram shows >= 1000 per class."],
        standards={"iso_pas_8800": ["6.2.3"], "eu_ai_act": ["Article 10"]},
    ),
    Requirement(
        id="REQ-SAFE-001",
        statement="The classifier shall flag low-confidence predictions below 0.6 threshold.",
        rationale="Safety mechanism: uncertain predictions routed to human operator.",
        verification_method="test",
        acceptance_criteria=["Predictions with max_prob < 0.6 are flagged."],
        standards={"iso_21448": ["7.1"], "ul_4600": ["8.5"]},
        priority="high",
    ),
]

display_requirements_table(requirements)
"""),

        # --- GtWR quality gate ---
        md("## 4. INCOSE GtWR Quality Gate"),
        code("""
print("Running GtWR quality gate on all requirements...\\n")

all_violations = []
for req in requirements:
    v = req.check_quality()
    all_violations.extend(v)
    icon = "PASS" if not v else f"FAIL ({len(v)} issues)"
    print(f"  {req.id}: {icon}")

print(f"\\nTotal: {len(all_violations)} violations across {len(requirements)} requirements")

if all_violations:
    display_violations_table(all_violations)
    plot_violations_by_rule(all_violations, "GtWR Violations (fix before proceeding)")
"""),

        # --- IO contracts ---
        md("""
## 5. Input-Output Contracts

An **IOContract** formalizes the interface between your ML component and the rest of the system — like a typed API contract but with runtime-checkable invariants.
"""),
        code("""
contract = IOContract(
    name="perception-classifier-io",
    description="Contract for the AV perception classifier.",
    inputs={
        "image": {"type": "tensor", "shape": [3, 640, 640], "dtype": "float32"},
        "confidence_threshold": {"type": "float", "range": [0.0, 1.0]},
    },
    outputs={
        "labels": {"type": "tensor", "shape": ["N"], "dtype": "int64"},
        "probabilities": {"type": "tensor", "shape": ["N", 4], "dtype": "float32"},
    },
    invariants=[
        Invariant(name="prob_range", description="Probabilities in [0,1]", check_expr="0 <= value <= 1"),
        Invariant(name="prob_sum", description="Probabilities sum to ~1", check_expr="abs(value - 1.0) < 0.01"),
        Invariant(name="label_valid", description="Labels in {0,1,2,3}", check_expr="value in (0, 1, 2, 3)"),
    ],
)

# Check invariants with sample values
sample_results = contract.check_invariants({
    "prob_range": 0.85,
    "prob_sum": 0.9999,
    "label_valid": 2,
})
print("Invariant checks:", sample_results)
"""),

        # --- HARA and ODD ---
        md("## 6. HARA and Operational Design Domain"),
        code("""
# Hazard Analysis and Risk Assessment
hazards = [
    Hazard(
        id="HAZ-001",
        description="Misclassification of pedestrian as background leads to collision.",
        severity="S3", exposure="E4", controllability="C2", asil="D",
        mitigations=["REQ-FUNC-001", "REQ-PERF-001", "REQ-SAFE-001"],
    ),
    Hazard(
        id="HAZ-002",
        description="Sensor noise degrades classification below safe threshold.",
        severity="S2", exposure="E3", controllability="C2", asil="B",
        mitigations=["REQ-ROB-001"],
    ),
]

# Operational Design Domain
odd = ODD(
    name="urban-driving-odd",
    dimensions={
        "speed_range_kmh": [0, 60],
        "weather": ["clear", "overcast", "light_rain"],
        "lighting": ["day", "dusk"],
        "road_type": ["urban_street", "parking_lot"],
        "traffic_density": ["low", "medium", "high"],
    },
    source_ontology="bsi_pas_1883",
)

print(f"ODD: {odd.name}")
print(f"Dimensions: {odd.dimension_names()}")
print(f"\\nHazards: {len(hazards)}")
for h in hazards:
    print(f"  {h.id} [{h.asil}]: {h.description[:60]}...")
"""),

        # --- Full spec assembly ---
        md("## 7. Assembling the Full Spec"),
        code("""
spec = Spec(
    name="av-perception-v1",
    version="0.3.0",
    requirements=requirements,
    contracts=[contract],
    odds=[odd],
    hazards=hazards,
)

print(f"Spec: {spec.name} v{spec.version}")
print(f"  Requirements: {len(spec.requirements)}")
print(f"  Contracts:    {len(spec.contracts)}")
print(f"  Hazards:      {len(spec.hazards)}")
print(f"  ODDs:         {len(spec.odds)}")
"""),

        # --- Evidence collection ---
        md("## 8. Simulated Evidence Collection"),
        code("""
# Simulate test results (in practice, these come from real test runs)
evidence = [
    Evidence(id="EV-FUNC-001", requirement_id="REQ-FUNC-001",
             kind="test", verdict="pass",
             details={"test_suite": "unit_tests", "samples": 5000}),
    Evidence(id="EV-PERF-001", requirement_id="REQ-PERF-001",
             kind="test", verdict="pass",
             details={"mAP": 0.891, "dataset": "val_v3"}),
    Evidence(id="EV-ROB-001", requirement_id="REQ-ROB-001",
             kind="test", verdict="fail",
             details={"precision": 0.63, "sigma": 0.1, "note": "Below 0.70 threshold"}),
    Evidence(id="EV-DATA-001", requirement_id="REQ-DATA-001",
             kind="inspection", verdict="pass",
             details={"min_class_count": 1247, "classes": 4}),
    Evidence(id="EV-SAFE-001", requirement_id="REQ-SAFE-001",
             kind="test", verdict="pass",
             details={"flagged_rate": 0.12, "threshold": 0.6}),
]

display_evidence_table(evidence)
"""),

        # --- Report ---
        md("## 9. Assessment Report"),
        code("""
report = Report(
    spec_name=spec.name,
    spec_version=spec.version,
    evidence=evidence,
    summary={"mAP": 0.891, "robustness_precision": 0.63},
)

display_report_summary(report)
plot_evidence_verdicts(report.evidence, "Assessment Verdicts")
"""),

        # --- Traceability ---
        md("## 10. Full Traceability Graph"),
        code("""
# Build links: evidence -> requirements -> hazards -> standards
links = [
    # Evidence verifies requirements
    TraceLink(source_id="EV-FUNC-001", target_id="REQ-FUNC-001", relation="verifies"),
    TraceLink(source_id="EV-PERF-001", target_id="REQ-PERF-001", relation="verifies"),
    TraceLink(source_id="EV-ROB-001", target_id="REQ-ROB-001", relation="verifies"),
    TraceLink(source_id="EV-DATA-001", target_id="REQ-DATA-001", relation="verifies"),
    TraceLink(source_id="EV-SAFE-001", target_id="REQ-SAFE-001", relation="verifies"),
    # Requirements mitigate hazards
    TraceLink(source_id="REQ-FUNC-001", target_id="HAZ-001", relation="mitigates"),
    TraceLink(source_id="REQ-PERF-001", target_id="HAZ-001", relation="mitigates"),
    TraceLink(source_id="REQ-SAFE-001", target_id="HAZ-001", relation="mitigates"),
    TraceLink(source_id="REQ-ROB-001", target_id="HAZ-002", relation="mitigates"),
]

plot_trace_graph(links)
"""),
        code("""
# Coverage report
graph = build_trace_graph(links)
cov = coverage_report(graph, [r.id for r in spec.requirements])
for req_id, linked in cov.items():
    print(f"{req_id}: {dict(linked)}")
"""),

        # --- Standards compliance ---
        md("## 11. Standards Compliance"),
        code("""
print("Mapped standards per requirement:\\n")
for req in spec.requirements:
    if req.standards:
        for std, clauses in req.standards.items():
            print(f"  {req.id} -> {std}: {clauses}")
"""),
        code("""
# Browse ISO/PAS 8800
display_registry_sample("iso_pas_8800", n=6)
"""),
        code("""
# EU AI Act Annex IV compliance document
annex_iv = export_annex_iv(report)
print(annex_iv[:1500])
print("\\n... (truncated)")
"""),

        # --- GSN ---
        md("## 12. Goal Structuring Notation (GSN) Assurance Case"),
        code("""
gsn = export_gsn_mermaid(report)
print(gsn)
display_mermaid(gsn)
"""),

        # --- Auto-generated tests ---
        md("## 13. Auto-Generated Test Suites"),
        code("""
# Generate pytest file from the spec
pytest_code = generate_pytest(spec)
print("=== Generated pytest file ===\\n")
print(pytest_code)
"""),
        code("""
# Generate hypothesis property tests from the contract
hyp_code = generate_hypothesis(contract)
print("=== Generated hypothesis tests ===\\n")
print(hyp_code)
"""),

        # --- Summary ---
        md("""
## Summary

| SE Artifact | vnvspec API | Output |
|------------|-------------|--------|
| Requirements document | `Spec(requirements=[...])` | Typed, machine-readable spec |
| FMEA / HARA | `Hazard(severity, exposure, ...)` | Hazard registry with ASIL |
| Traceability matrix | `TraceLink` + `build_trace_graph()` | Interactive graph + coverage |
| Test procedures | `generate_pytest(spec)` | Runnable pytest file |
| V&V report | `Report(evidence=[...])` | HTML, Markdown, JSON |
| Compliance doc | `export_annex_iv(report)` | EU AI Act Annex IV draft |
| Assurance case | `export_gsn_mermaid(report)` | GSN diagram (Mermaid) |

**Next:** See Notebook 3 for PyTorch model wrapping and automated assessment.
"""),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# NOTEBOOK 3 — ML Expert
# ═══════════════════════════════════════════════════════════════════════════

def nb_ml_expert() -> dict:
    return notebook([
        md("""
# Specifying & Verifying Your ML Models

**Audience:** ML practitioners who want to add V&V rigor to their models without learning an entirely new discipline.

**What you'll learn:**
1. How to wrap a PyTorch model for automated assessment
2. How to define specs with concrete, testable criteria
3. How to run assessments and generate compliance reports
4. How hook-based inspection and property testing work

**Prerequisites:** PyTorch installed (`pip install vnvspec[torch]`)

**Time:** ~30 minutes

---
"""),

        # --- Setup ---
        md("## 1. Setup"),
        code("""
import sys, os
sys.path.insert(0, os.path.abspath(".."))

import torch
import torch.nn as nn
print(f"PyTorch: {torch.__version__}")

import vnvspec
print(f"vnvspec: {vnvspec.__version__}")

from vnvspec import Spec, Requirement, Evidence, IOContract, Invariant
from vnvspec.core.assessment import Report
from vnvspec.torch import TorchAdapter, HookManager, SampleBudgetIterator
from vnvspec.exporters import export_html, export_markdown, export_gsn_mermaid
from vnvspec.runners.pytest_gen import generate_pytest

from _helpers import (
    display_requirements_table, display_evidence_table,
    display_report_summary, display_violations_table,
    plot_evidence_verdicts, plot_coverage,
    display_mermaid, display_registry_sample,
)
print("All imports ready.")
"""),

        # --- Why specs? ---
        md("""
## 2. Why Specs Matter for ML

You wouldn't deploy a web service without an API contract. Yet ML models routinely ship with nothing more than "accuracy = 0.94 on test set."

**What can go wrong without specs:**
- Model outputs NaN under certain inputs (silent failure)
- Probability outputs > 1.0 after a "harmless" refactor
- Latency regresses 10x after adding a new layer
- Model works perfectly on English but fails on Arabic

**A spec is your model's contract with the rest of the system.**
"""),

        # --- Build a model ---
        md("## 3. Build a Simple Model"),
        code("""
class TabularMLP(nn.Module):
    \"\"\"3-layer MLP for tabular classification (10 features -> 3 classes).\"\"\"

    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(10, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 3),
            nn.Softmax(dim=-1),
        )

    def forward(self, x):
        return self.layers(x)

model = TabularMLP()
print(model)
print(f"\\nParameters: {sum(p.numel() for p in model.parameters()):,}")
"""),

        # --- Define the spec ---
        md("## 4. Define the Spec"),
        code("""
spec = Spec(
    name="tabular-mlp-v1",
    version="1.0.0",
    requirements=[
        Requirement(
            id="REQ-PROB",
            statement="The model shall produce probabilities in [0.0, 1.0].",
            rationale="Downstream decision logic assumes valid probabilities.",
            verification_method="test",
            acceptance_criteria=["All output values in [0.0, 1.0]."],
            priority="high",
        ),
        Requirement(
            id="REQ-SUM",
            statement="The model shall produce probabilities that sum to 1.0 within 0.01 tolerance.",
            rationale="Probability simplex constraint.",
            verification_method="test",
            acceptance_criteria=["abs(sum(probs) - 1.0) < 0.01 for all samples."],
        ),
        Requirement(
            id="REQ-DIM",
            statement="The model shall output exactly 3 class scores per sample.",
            rationale="3-class classification task.",
            verification_method="test",
            acceptance_criteria=["Output shape[-1] == 3."],
        ),
        Requirement(
            id="REQ-NAN",
            statement="The model shall not produce NaN or Inf values in any output.",
            rationale="NaN propagation causes silent downstream failures.",
            verification_method="test",
            acceptance_criteria=["No NaN or Inf in output tensor."],
            priority="high",
        ),
        Requirement(
            id="REQ-DETERMINISTIC",
            statement="The model shall produce identical outputs for identical inputs in eval mode.",
            rationale="Reproducibility for debugging and auditing.",
            verification_method="test",
            acceptance_criteria=["output1 == output2 for same input."],
        ),
    ],
)

# Quality gate
all_v = []
for r in spec.requirements:
    all_v.extend(r.check_quality())
print(f"GtWR violations: {len(all_v)}")
display_requirements_table(spec.requirements)
"""),

        # --- Wrap with TorchAdapter ---
        md("""
## 5. Wrap with TorchAdapter

`TorchAdapter` wraps your `nn.Module` and provides the `ModelAdapter` protocol:
"""),
        code("""
adapter = TorchAdapter(
    model,
    device="cpu",
    sample_budget=500,
    batch_size=64,
)

print(f"Adapter info: {adapter.describe()}")
print(f"Batch size hint: {adapter.batch_size_hint()}")
print(f"Streaming: {adapter.supports_streaming()}")
"""),

        # --- Manual forward pass ---
        md("## 6. Manual Verification"),
        code("""
# Generate test data
test_data = [torch.randn(10) for _ in range(500)]

# Quick manual checks
sample_batch = torch.stack(test_data[:16])
output = adapter.forward(sample_batch)

print(f"Input shape:  {sample_batch.shape}")
print(f"Output shape: {output.shape}")
print(f"Output range: [{output.min():.6f}, {output.max():.6f}]")
print(f"Sum per row:  {output.sum(dim=-1)[:5]}")
print(f"Any NaN:      {output.isnan().any()}")
print(f"Any Inf:      {output.isinf().any()}")
"""),

        # --- Automated assessment ---
        md("""
## 7. Automated Assessment

`adapter.assess()` runs the model on all data, evaluates each requirement, and produces a `Report`:
"""),
        code("""
report = adapter.assess(spec, test_data)

display_report_summary(report)
display_evidence_table(report.evidence)
"""),
        code("""
plot_evidence_verdicts(report.evidence, "Model Assessment Results")
"""),

        # --- Hook-based inspection ---
        md("""
## 8. Hook-Based Layer Inspection

`HookManager` lets you observe activations at any layer — useful for debugging NaN propagation, checking activation ranges, or monitoring gradient flow.
"""),
        code("""
hm = HookManager(summary_mode=True)
hm.attach(model)

# Run a batch
with torch.no_grad():
    _ = model(torch.randn(8, 10))

# Check observations
print(f"Observed layers: {list(hm.observations.keys())}\\n")
for layer_name, summaries in hm.observations.items():
    s = summaries[0]  # first (and only) observation
    print(f"{layer_name}:")
    print(f"  shape={s.shape}, dtype={s.dtype}")
    print(f"  min={s.min_val:.4f}, max={s.max_val:.4f}, mean={s.mean_val:.4f}")
    print(f"  NaN count: {s.nan_count}")
    print()

hm.detach()
"""),

        # --- Custom verification ---
        md("""
## 9. Custom Verification with Evidence

For domain-specific checks, create `Evidence` objects directly:
"""),
        code("""
import time

# Latency benchmark
model.eval()
times = []
for _ in range(100):
    x = torch.randn(1, 10)
    t0 = time.perf_counter()
    with torch.no_grad():
        _ = model(x)
    times.append((time.perf_counter() - t0) * 1000)  # ms

p50 = sorted(times)[50]
p99 = sorted(times)[99]

ev_latency = Evidence(
    id="EV-LATENCY",
    requirement_id="REQ-DETERMINISTIC",  # closest match
    kind="test",
    verdict="pass" if p99 < 50 else "fail",
    details={"p50_ms": round(p50, 3), "p99_ms": round(p99, 3), "runs": 100},
)

print(f"Latency p50: {p50:.3f} ms, p99: {p99:.3f} ms")
print(f"Verdict: {ev_latency.verdict}")
"""),

        # --- Determinism check ---
        code("""
# Determinism check
x = torch.randn(4, 10)
model.eval()
with torch.no_grad():
    out1 = model(x)
    out2 = model(x)

is_deterministic = torch.equal(out1, out2)
ev_determinism = Evidence(
    id="EV-DETERMINISM",
    requirement_id="REQ-DETERMINISTIC",
    kind="test",
    verdict="pass" if is_deterministic else "fail",
    details={"max_diff": float((out1 - out2).abs().max())},
)

print(f"Deterministic: {is_deterministic} (max diff: {(out1 - out2).abs().max():.2e})")
"""),

        # --- Enhanced report ---
        md("## 10. Enhanced Report with Custom Evidence"),
        code("""
# Combine automated + custom evidence
all_evidence = list(report.evidence) + [ev_latency, ev_determinism]

enhanced_report = Report(
    spec_name=spec.name,
    spec_version=spec.version,
    evidence=all_evidence,
    summary={
        "samples": 500,
        "latency_p99_ms": round(p99, 3),
        "deterministic": is_deterministic,
    },
)

display_report_summary(enhanced_report)
display_evidence_table(enhanced_report.evidence)
plot_evidence_verdicts(enhanced_report.evidence, "Complete Assessment")
"""),

        # --- Export ---
        md("## 11. Export Reports"),
        code("""
# HTML report (standalone, no external deps)
html = export_html(enhanced_report)
print(f"HTML report: {len(html)} chars")
print(html[:500])
print("...")
"""),
        code("""
# GSN assurance case
gsn = export_gsn_mermaid(enhanced_report)
print(gsn)
display_mermaid(gsn)
"""),

        # --- Auto-generate tests ---
        md("## 12. Auto-Generated Test Suite"),
        code("""
pytest_code = generate_pytest(spec)
print(pytest_code)
"""),
        md("""
Save this to a `.py` file and run `pytest` — you get a runnable test suite derived directly from your spec.
"""),

        # --- Standards context ---
        md("## 13. Standards Context (Why This Matters)"),
        code("""
display_registry_sample("nist_ai_rmf", n=6)
"""),
        md("""
These standards increasingly **require** the kind of evidence trail we just built:
- **ISO/PAS 8800**: AI safety for vehicles — requires documented V&V evidence
- **EU AI Act**: High-risk AI systems must produce technical documentation (Annex IV)
- **NIST AI RMF**: Govern → Map → Measure → Manage — requires traceable risk management

`vnvspec` gives you the data structures and export formats to satisfy these requirements without changing your ML workflow.
"""),

        # --- Summary ---
        md("""
## Summary: Your V&V Workflow

```
1. Define spec      Spec(requirements=[...])
2. Wrap model       TorchAdapter(model)
3. Run assessment   adapter.assess(spec, data) -> Report
4. Inspect layers   HookManager.attach(model)
5. Custom checks    Evidence(..., verdict="pass")
6. Export           export_html(report), export_gsn_mermaid(report)
7. Generate tests   generate_pytest(spec) -> runnable .py file
```

**The key insight:** V&V isn't about slowing down your ML workflow — it's about making your model's contract explicit and automatically verifiable.
"""),
    ])


# ═══════════════════════════════════════════════════════════════════════════
# Generate all notebooks
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Generating notebooks...")
    save(nb_student(), "01_student_intro.ipynb")
    save(nb_se_pro(), "02_se_professional.ipynb")
    save(nb_ml_expert(), "03_ml_expert.ipynb")
    print("Done!")
