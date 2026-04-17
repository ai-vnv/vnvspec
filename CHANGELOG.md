# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.1.0] — 2026-04-17

### Added

- Core models: `Spec`, `Requirement`, `Evidence`, `Hazard`, `ODD`, `IOContract`, `TraceLink`.
- INCOSE GtWR requirement quality checker (`Requirement.check_quality()`).
- Assessment engine with `AssessmentContext` and `Report`.
- `TorchAdapter` for wrapping `nn.Module` models.
- `TransformerAdapter` for HuggingFace encoder/seq2seq models.
- `AutoregressiveAdapter` and `VLMAdapter` for generative models.
- `HookManager` for activation and gradient inspection.
- `SampleBudgetIterator` for budget-aware batching with OOM recovery.
- Exporters: HTML, JSON, Markdown, GSN/Mermaid, EU AI Act Annex IV.
- CLI via `vnvspec` command (powered by Typer).
- Validators and registries subsystems.
- Full CI pipeline (lint, typecheck, test matrix).
- PyPI trusted-publisher release workflow.
- MkDocs Material documentation site with GitHub Pages deployment.
- Examples: tabular MLP quick-start, BERT-tiny sentiment classification.
- Initial project scaffolding and tooling.
