# vnvspec

**V&V-grade specifications for engineered systems -- AI, optimization, simulation, and physics.**

## Overview

vnvspec is a Python library for writing machine-readable verification and validation (V&V) specifications. You define requirements, input-output contracts, operational design domains, and hazards using typed Pydantic models, then assess models against those specs to produce traceable evidence reports.

The library maps directly to international safety and AI standards including ISO/PAS 8800, ISO 21448 (SOTIF), UL 4600, the EU AI Act, and NIST AI RMF.

## Key Features

- **Typed spec language** -- `Spec`, `Requirement`, `IOContract`, `ODD`, `Hazard`, `Evidence` models built on Pydantic
- **INCOSE GtWR quality checker** -- catch vague, ambiguous, or unverifiable requirements early via `Requirement.check_quality()`
- **Traceability graphs** -- link requirements to hazards, evidence, and standards clauses with `TraceLink` and `build_trace_graph()`
- **Standards registries** -- built-in clause databases for five major standards
- **Pluggable adapters** -- wrap PyTorch, HuggingFace, and other models via the `ModelAdapter` protocol
- **Auto-generated tests** -- emit pytest and Hypothesis property tests from specs
- **Rich exports** -- HTML reports, Markdown, GSN assurance cases (Mermaid), EU AI Act Annex IV tech docs

## Quick Start

```python
from vnvspec import Requirement, Spec

req = Requirement(
    id="REQ-001",
    statement="The classifier shall produce probabilities in [0, 1].",
    rationale="Probability outputs must be valid for downstream calibration.",
    verification_method="test",
    acceptance_criteria=["All output probabilities are between 0.0 and 1.0."],
)

spec = Spec(name="image-classifier-v1", requirements=[req])
violations = req.check_quality()
print(f"Quality issues: {len(violations)}")
```

## Installation

```bash
pip install vnvspec          # core library
pip install vnvspec[torch]   # with PyTorch adapter
pip install vnvspec[docs]    # with documentation tooling
pip install vnvspec[all]     # everything
```

## API Reference

The public API is importable from the top-level `vnvspec` package:

| Class | Module | Purpose |
|-------|--------|---------|
| `Spec` | `vnvspec.core.spec` | Top-level specification container |
| `Requirement` | `vnvspec.core.requirement` | Single verifiable requirement |
| `IOContract` | `vnvspec.core.contract` | Input-output contract with invariants |
| `Evidence` | `vnvspec.core.evidence` | Verification activity record |
| `Hazard` | `vnvspec.core.hazard` | Identified hazard |
| `ODD` | `vnvspec.core.odd` | Operational design domain |
| `TorchAdapter` | `vnvspec.torch.adapter` | PyTorch model adapter |
