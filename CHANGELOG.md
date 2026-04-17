# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

## [0.2.0] — Unreleased

### Added

- `Evidence.details` now accepts `str | dict` — bare strings are auto-wrapped to `{"message": "..."}`.
- `Report.summary` now accepts `str | dict` — same auto-wrap behavior.
- Structured CLI exit codes: 0 (OK), 1 (failures), 2 (inconclusive), 3 (spec validation error), 4 (usage error), 5 (internal error).
- `ExitCode` enum exported from `vnvspec.cli.main`.
- Deprecation infrastructure (`vnvspec._deprecation.deprecated` decorator) for future symbol lifecycle management.
- `EvidenceCollector` context manager for ergonomic evidence collection with `check()`, `record()`, and `from_pytest_junit()` methods.
- `EvidenceCollector` and `Report` now exported from `vnvspec` top-level.
- `vnvspec.catalog` namespace (preview) and `vnvspec.catalog.demo` demo module.
- `Spec.extend(*requirements)` for composing catalog modules into a spec.
- YAML/TOML/JSON spec I/O: `Spec.from_yaml()`, `Spec.to_yaml()`, `Spec.from_toml()`, `Spec.to_toml()`, `Spec.from_json()`, `Spec.to_json()`.
- `vnvspec init --format yaml|toml|py` flag for scaffolding specs in different formats.
- New dependencies: `pyyaml>=6.0`, `tomli-w>=1.0`, `openpyxl>=3.1`.
- Compliance matrix exporter (`export_compliance_matrix()`) in XLSX, CSV, and HTML formats.
- `standard_gap_analysis()` for analyzing spec coverage against standards registries.
- `GapReport` and `ClauseCoverage` models for structured gap analysis results.
- Configurable GtWR rule profiles: `formal` (default), `web-app`, `embedded`.
- `RuleViolation.severity` now includes `"info"` level alongside `"error"` and `"warning"`.
- `Requirement.check_quality(profile=...)` parameter for per-project profile selection.
- CLI `vnvspec validate --profile web-app` flag.
- `pytest-vnvspec` plugin (separate subpackage at `packages/pytest-vnvspec/`).
  - `@pytest.mark.vnvspec("REQ-001")` marker to link tests to requirements.
  - `--vnvspec-spec`, `--vnvspec-report`, `--vnvspec-fail-on` CLI options.
  - Auto-generates inconclusive evidence for unlinked test requirements.
  - Validates marker references at collection time.
- `auto_trace()` for regex-based requirement-to-code traceability scanning.
- `vnvspec.trace` subpackage for automated traceability utilities.
- Badge SVG exporter (`export_badge()`) — locally generated, no external service.
- Report diff (`compare_reports()`) for evidence regression detection between reports.
- `ReportDiff` model with `new_failures`, `regressions`, `added_requirements`, etc.
- GitHub Actions composite action at `actions/vnvspec/action.yml`.

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
