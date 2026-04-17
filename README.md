# vnvspec

V&V-grade specifications for engineered systems — AI, optimization, simulation, and physics.

[![CI](https://github.com/ai-vnv/vnvspec/actions/workflows/ci.yml/badge.svg)](https://github.com/ai-vnv/vnvspec/actions/workflows/ci.yml)
[![Docs](https://github.com/ai-vnv/vnvspec/actions/workflows/docs.yml/badge.svg)](https://ai-vnv.github.io/vnvspec/)
[![codecov](https://codecov.io/gh/ai-vnv/vnvspec/graph/badge.svg)](https://codecov.io/gh/ai-vnv/vnvspec)
[![V&Ved](https://raw.githubusercontent.com/ai-vnv/vnvspec/release/0.2.0/.vnvspec/dashboard/badge.svg)](https://ai-vnv.github.io/vnvspec/dashboard/)
[![PyPI](https://img.shields.io/pypi/v/vnvspec)](https://pypi.org/project/vnvspec/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-≥3.11-blue.svg)](https://python.org)

## Overview

**vnvspec** lets you write machine-readable V&V specifications for any engineered system
and automatically assess models against them. It produces traceable evidence reports
that map to international standards (ISO/PAS 8800, ISO 21448, UL 4600, EU AI Act, and more).

### Key features

- **Typed spec language** — Pydantic-based `Spec`, `Requirement`, `IOContract`, `ODD`, `Hazard`, `Evidence` models
- **INCOSE GtWR quality checker** — catch vague, ambiguous, or unverifiable requirements early, with configurable profiles (formal, web-app, embedded)
- **Traceability graphs** — link requirements ↔ hazards ↔ evidence ↔ standards clauses, plus auto-trace scanning
- **Standards registries** — built-in clause databases for ISO/PAS 8800, ISO 21448, UL 4600, EU AI Act, NIST AI RMF
- **Compliance matrix** — auditor-grade XLSX/CSV/HTML exports with gap analysis against any standard
- **Pluggable adapters** — wrap any model (PyTorch, HuggingFace, scikit-learn, ONNX, Pyomo, FMI)
- **EvidenceCollector** — ergonomic context manager for building evidence from assertions and JUnit XML
- **pytest plugin** — `pytest-vnvspec` captures evidence directly from test results
- **Multi-format specs** — define specs in Python, YAML, or TOML; lossless round-trips
- **CI integrations** — GitHub Actions composite action, V&V badge SVG, report diff for regression detection
- **Rich exports** — HTML reports, Markdown, GSN assurance cases (Mermaid), EU AI Act Annex IV tech docs

## Installation

```bash
pip install vnvspec
```

With PyTorch adapter:

```bash
pip install vnvspec[torch]
```

## Quick start

```python
from vnvspec import Requirement, Spec

req = Requirement(
    id="REQ-001",
    statement="The classifier shall produce probabilities in [0, 1].",
    rationale="Probability outputs must be valid for downstream calibration.",
    verification_method="test",
    acceptance_criteria=["All output probabilities are between 0.0 and 1.0 inclusive."],
)

spec = Spec(name="image-classifier-v1", requirements=[req])
violations = req.check_quality()
print(f"Quality issues: {len(violations)}")
```

## Development

```bash
# Install all dev dependencies
just install

# Run all checks (lint, typecheck, test with coverage)
just check
```

## License

Apache-2.0. See [LICENSE](LICENSE).
