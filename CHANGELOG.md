# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Changed

- **Behavior change (may affect CI):** `Report.verdict()` now returns `"inconclusive"` when any inconclusive evidence is present and no failures. Previously returned `"pass"` in this case. Pass `verdict_policy="lenient"` to restore old behavior. This change aligns `Report.verdict()` with the existing CLI exit-code semantics (`ExitCode.INCONCLUSIVE = 2`).

### Added

- `Report.verdict_policy` field (`"strict"` | `"lenient"`) to control inconclusive roll-up behavior.
- `Report.inconclusive_count()` method for counting inconclusive evidence.
- `"formal_proof"` as a valid `VerificationMethod` and `EvidenceKind` value (vocabulary reserved for v0.4 formal-methods integration; no adapter implementation yet).
- `Requirement.source` now accepts `list[str]` (multiple URLs) in addition to `str` (auto-normalized to a one-element list). Empty string normalizes to `[]`.
- `scripts/check_v0_2_compat.py` for v0.2 backward-compatibility enforcement in CI.
- Catalog test fixture infrastructure (`tests/catalog/conftest.py`) with `validate_catalog_requirement()` for auto-testing catalog modules against the inclusion policy.
- Catalog infrastructure (`vnvspec.catalog._base`) with `discover_catalogs()`, `all_requirements()`, `check_compatibility()`, and `CatalogInfo`/`CompatibilityReport` dataclasses.
- `vnvspec catalog list` — list all discovered catalog modules with requirement counts and version pins.
- `vnvspec catalog show <module>` — show requirements from a catalog module.
- `vnvspec catalog audit` — audit catalog modules for compatibility with installed packages.
- `vnvspec catalog import <module>` — export catalog requirements to YAML/TOML/JSON.
- New dependency: `packaging>=23`.
- `CONTRIBUTING-CATALOG.md` — inclusion policy for catalog modules (six-criteria gate).
- `vnvspec.catalog.ml.pytorch_training` — 30 curated best-practice requirements across 5 sub-modules: `reproducibility` (6), `gradient_health` (6), `checkpointing` (6), `data_loading` (6), `loss_validation` (6). Sources: PyTorch docs, Karpathy's Recipe, NIST AI RMF.
- `vnvspec.catalog.ml.huggingface_inference` — 24 requirements across 4 sub-modules: `tokenization` (6), `generation` (6), `attention_masks` (6), `structured_outputs` (6). Sources: HuggingFace Transformers docs, Vaswani et al.
- `vnvspec.catalog.web.fastapi` — 22 requirements across 3 sub-modules: `security` (10, OWASP API Top 10 2023 mapped), `observability` (6), `api_design` (6). Sources: OWASP API Security 2023, FastAPI docs, RFC 9457.
- `vnvspec.catalog.web.sqlalchemy` — 18 requirements across 3 sub-modules: `transactions` (6), `session` (6), `schema` (6). Sources: SQLAlchemy 2.0 docs, Alembic docs, Cosmic Python.
- `vnvspec.catalog.optimization.pyomo` — 19 requirements across 3 sub-modules: `solver_status` (6), `constraint_validation` (7), `model_invariants` (6). Sources: Pyomo docs, Hart et al., Williams.
- Standards mappings across all catalogs: NASA SE Handbook (SP-2016-6105), INCOSE SE Handbook, IEEE 754-2019, ISO/IEC 25010:2023, DO-178C, SAE ARP4754A, SAE J3131, ISO/SAE 21434. 10 standards frameworks total, 75% of requirements mapped.
- 4 new IEEE 754 floating-point requirements: gradient overflow/underflow detection (PyTorch), numerically stable loss functions (PyTorch), mixed-precision dtype consistency (HuggingFace), compensated summation (Pyomo).
- `docs/catalog/standards-mapping.md` — comprehensive reference for all standards mappings.

## [0.2.0] — 2026-04-17

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
- V&V dashboard exporter (`export_dashboard()`) — static HTML site with per-requirement detail pages, standards compliance table, version history timeline, clickable badge.
- Badge SVG now supports `dashboard_url` parameter for clickable links.
- Self-specification at `.vnvspec/self-spec.yaml` with 26 requirements (8 from v0.1, 18 from v0.2), all with `metadata.since` version tracking.
- Self-assessment via `vnvspec assess --self` and `pytest --vnvspec-spec=.vnvspec/self-spec.yaml`.
- `scripts/check_v0_1_compat.py` for backward-compatibility enforcement in CI.

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
