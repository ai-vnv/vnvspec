# Architecture

This page describes the high-level architecture of vnvspec.

## Package Structure

```
src/vnvspec/
    __init__.py          # Public API re-exports
    _version.py          # Version string
    core/                # Core data models
        spec.py          # Spec -- top-level container
        requirement.py   # Requirement with GtWR quality checks
        contract.py      # IOContract and Invariant
        evidence.py      # Evidence records
        assessment.py    # AssessmentContext and Report
        hazard.py        # Hazard model (severity, ASIL)
        odd.py           # Operational Design Domain
        trace.py         # TraceLink, build_trace_graph, coverage_report
        protocols.py     # ModelAdapter, Exporter, TestRunner protocols
        errors.py        # Exception hierarchy
        _internal/       # Private implementation details
            gtwr_rules.py  # INCOSE GtWR rule engine
    torch/               # PyTorch adapter
        adapter.py       # TorchAdapter
        transformer.py   # TransformerAdapter (HuggingFace)
        autoregressive.py # AutoregressiveAdapter
        vlm.py           # VLMAdapter (vision-language)
        hooks.py         # HookManager for activation inspection
        sampling.py      # SampleBudgetIterator
    registries/          # Standards clause databases
        loader.py        # Registry loading utilities
    validators/          # Schema validation adapters
        pydantic_adapter.py
        pandera_adapter.py
    exporters/           # Output format generators
        markdown.py      # Markdown export
        html.py          # HTML report export
        json_export.py   # JSON export
        gsn_mermaid.py   # GSN assurance case diagrams
        techdoc_annex_iv.py  # EU AI Act Annex IV
    runners/             # Test generation
        pytest_gen.py    # Generate pytest test files
        hypothesis_gen.py # Generate Hypothesis property tests
    cli/                 # Command-line interface
        main.py          # CLI entry point
```

## Design Principles

**Immutable models.** All core models (`Spec`, `Requirement`, `IOContract`, `Evidence`, `Hazard`, `ODD`) are frozen Pydantic models. This ensures specs are tamper-proof once constructed and safe to share across threads.

**Protocol-based extensibility.** The `ModelAdapter`, `Exporter`, and `TestRunner` protocols in `vnvspec.core.protocols` define the extension points. New adapters (e.g., for scikit-learn or ONNX) implement `ModelAdapter` without modifying core code.

**Layered architecture.** The core layer has zero framework dependencies beyond Pydantic and NetworkX. The torch adapter is an optional dependency. Exporters and runners depend only on the core layer.

**Standards-aware traceability.** Requirements link to standards clauses via the `standards` dict field. The `TraceLink` model and `build_trace_graph()` function construct a NetworkX directed graph connecting requirements, hazards, evidence, and standards clauses for full traceability analysis.

## Dependency Graph

```
core (pydantic, networkx)
  |
  +-- torch adapter (torch, transformers)
  +-- validators (pandera)
  +-- exporters (no extra deps)
  +-- runners (no extra deps)
  +-- registries (no extra deps)
  +-- cli (no extra deps)
```

## Extension Points

To add a new model adapter, implement the `ModelAdapter` protocol from `vnvspec.core.protocols`. To add a new exporter, implement the `Exporter` protocol. Both are structural (duck-typed) protocols -- no inheritance required.
