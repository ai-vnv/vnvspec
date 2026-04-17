# vnvspec — Phase Progress

| Phase | Description | Status | Last Check |
|-------|-------------|--------|------------|
| 1 | Repo bootstrap + tooling | COMPLETE | 2026-04-17 — just check passes, uv build produces wheel |
| 2 | Core data model | COMPLETE | 2026-04-17 — 51 core tests pass, ≥90% coverage on core/ |
| 3 | INCOSE GtWR rule checker | COMPLETE | 2026-04-17 — 27 GtWR tests (8 pass + 8 fail + integration), 100% coverage |
| 4 | Traceability graph + Wave A | COMPLETE | 2026-04-17 — 12 trace tests, GraphML round-trip, Wave A report generated |
| 5 | Standards registry loader | COMPLETE | 2026-04-17 — 5 JSON bundles (164 entries), 27 tests |
| 6 | Validators | COMPLETE | 2026-04-17 — pydantic + pandera adapters, 13 tests |
| 7 | Protocols | COMPLETE | 2026-04-17 — ModelAdapter, TestRunner, Exporter + AssessmentContext/Report |
| 8 | PyTorch base adapter | COMPLETE | 2026-04-17 — TorchAdapter + hooks + sampling, 19 tests |
| 9 | Transformer adapter | COMPLETE | 2026-04-17 — TransformerAdapter for HF encoders |
| 10 | Autoregressive + VLM adapters | COMPLETE | 2026-04-17 — AutoregressiveAdapter + VLMAdapter |
| 11 | Runners | COMPLETE | 2026-04-17 — pytest_gen + hypothesis_gen |
| 12 | Exporters | COMPLETE | 2026-04-17 — HTML, MD, GSN Mermaid, Annex IV, JSON |
| 13 | CLI | COMPLETE | 2026-04-17 — vnvspec command with init/validate/export/registries |
| 14 | Docs site | COMPLETE | 2026-04-17 — MkDocs Material with 13 doc pages |
| 15 | Integration tests + examples | COMPLETE | 2026-04-17 — 2 examples (tabular MLP, BERT sentiment) |
| 16 | Packaging, CI, release | COMPLETE | 2026-04-17 — CI/release/docs workflows, CHANGELOG 0.1.0, uv build OK |
