# Standards Mapping Reference

This document summarizes the standards frameworks mapped across vnvspec catalog requirements, covering NASA, INCOSE, SAE, IEEE, ISO, and OWASP standards.

## Standards Frameworks

| Key | Standard | Scope |
|-----|----------|-------|
| `nist_ai_rmf` | NIST AI Risk Management Framework (AI 100-1) | AI/ML governance, measurement, monitoring |
| `owasp_api_top10_2023` | OWASP API Security Top 10 2023 | API security vulnerabilities |
| `ieee_754` | IEEE 754-2019 / ISO/IEC 60559 | Floating-point arithmetic, NaN/Inf, reproducibility |
| `iso_25010` | ISO/IEC 25010:2023 (SQuaRE) | Software product quality model |
| `nasa_se_handbook` | NASA SP-2016-6105 Rev2 (SE Handbook) | Systems engineering processes, V&V, config management |
| `incose_se_handbook` | INCOSE Systems Engineering Handbook | SE processes, measurement, quality assurance |
| `do_178c` | DO-178C (RTCA) | Software verification for airborne systems |
| `sae_arp4754a` | SAE ARP4754A | Development assurance, system-level V&V |
| `sae_j3131` | SAE J3131 | V&V of automated driving systems, coverage metrics |
| `iso_sae_21434` | ISO/SAE 21434:2021 | Cybersecurity engineering for road vehicles |

## Clause Mappings by Standard

### NASA SE Handbook (SP-2016-6105 Rev2)

| Clause | Title | Catalogs Using It |
|--------|-------|-------------------|
| 5.3 | Product Verification | PyTorch (reproducibility, gradient, loss), Pyomo (solver, constraint, invariants), SQLAlchemy (transactions) |
| 5.4 | Product Validation | Pyomo (known-solution test) |
| 6.5 | Configuration Management | PyTorch (version logging, checkpointing), HuggingFace (tokenizer pinning, generation config), FastAPI (security misconfiguration), Pyomo (solver availability/version), SQLAlchemy (Alembic migrations) |

### INCOSE SE Handbook

| Clause | Title | Catalogs Using It |
|--------|-------|-------------------|
| 5.5 | Configuration Management Process | PyTorch (version logging), HuggingFace (tokenizer pinning), Pyomo (solver version), SQLAlchemy (migrations) |
| 5.7 | Measurement Process | PyTorch (gradient norms), FastAPI (observability/metrics), Pyomo (solver metrics, worst violation, model complexity), HuggingFace (data logging) |

### IEEE 754-2019 (Floating-Point Arithmetic)

| Clause | Title | Catalogs Using It |
|--------|-------|-------------------|
| 4.3 | Rounding-direction attributes | Pyomo (validation tolerance) |
| 5.3 | Computational operations | Pyomo (objective cross-check, dimensional consistency) |
| 5.4 | formatOf operations (type conversion) | HuggingFace (attention mask precision) |
| 5.7 | Non-computational operations (isNaN, isFinite) | PyTorch (NaN/Inf gradient detection, finite loss check) |
| 5.8 | FP-to-integer conversions | Pyomo (integer variable integrality) |
| 6.1 | Infinity arithmetic | PyTorch (NaN/Inf detection, numerical stability) |
| 6.2 | Operations with NaNs | PyTorch (NaN gradient propagation) |
| 7.1 | Exception flags overview | PyTorch (finite loss check), Pyomo (constraint validation) |
| 7.4 | Overflow | PyTorch (gradient overflow detection) |
| 7.5 | Underflow | PyTorch (gradient underflow detection) |
| 9.4 | Reduction operations (sum, dot) | Pyomo (compensated summation for constraint evaluation) |
| 11 | Reproducible FP results | PyTorch (seed all RNGs, deterministic algorithms, dataset reproducibility) |

### ISO/IEC 25010:2023 (SQuaRE Product Quality)

| Clause | Title | Catalogs Using It |
|--------|-------|-------------------|
| 4.1.2 | Functional Correctness | HuggingFace (tokenizer round-trip, stop tokens, attention shape, JSON validation), Pyomo (termination check, bounds, dimensional consistency, summation, known-solution), PyTorch (numerical stability) |
| 4.2.1 | Time Behavior | FastAPI (metrics), SQLAlchemy (narrow transactions), Pyomo (solver time limit) |
| 4.2.2 | Resource Utilization | SQLAlchemy (pool sizing) |
| 4.2.3 | Capacity | SQLAlchemy (pool sizing) |
| 4.5.1 | Faultlessness | PyTorch (NaN/Inf detection, finite loss, overflow/underflow), FastAPI (idempotency), HuggingFace (JSON validation) |
| 4.5.2 | Availability | FastAPI (health/ready probes), SQLAlchemy (pool_pre_ping) |
| 4.5.3 | Fault Tolerance | HuggingFace (adversarial inputs, retry), FastAPI (unsafe consumption), SQLAlchemy (retry with backoff), Pyomo (infeasible/unbounded handling) |
| 4.5.4 | Recoverability | PyTorch (reproducibility), SQLAlchemy (rollback, migration rollback) |
| 4.6.1 | Confidentiality | FastAPI (BOPLA, sensitive logging), SQLAlchemy (session isolation) |
| 4.6.2 | Integrity | PyTorch (checkpoint integrity), SQLAlchemy (transactions) |
| 4.6.4 | Accountability | FastAPI (BOLA authorization) |
| 4.6.5 | Authenticity | FastAPI (broken authentication) |
| 4.6.6 | Resistance | FastAPI (security misconfiguration, input validation) |
| 4.7.3 | Analysability | HuggingFace (error preservation), FastAPI (structured logging, correlation IDs), Pyomo (solver metrics) |

### DO-178C (Software Verification)

| Clause | Title | Catalogs Using It |
|--------|-------|-------------------|
| 6.1 | Requirements-based testing | PyTorch (first-step baseline, overfit batch, trainable params), HuggingFace (tokenizer round-trip, special tokens, attention shape), Pyomo (termination check, constraint validation, objective sense, Param vs Var, known-solution) |
| 6.3 | Test coverage analysis | PyTorch (reproducibility, dataset reproducibility), Pyomo (known-solution coverage) |

### SAE Standards

| Standard | Clause | Title | Catalogs Using It |
|----------|--------|-------|-------------------|
| ARP4754A | 7 | Validation and Verification | Pyomo (infeasible/unbounded handling) |
| ARP4754A | 8 | Configuration Management | PyTorch (checkpointing) |
| J3131 | 10.1 | Coverage Metrics | PyTorch (first-step loss baseline), Pyomo (known-solution test) |
| ISO/SAE 21434 | 10 | Product Development (Cybersecurity V&V) | FastAPI (BOLA, SSRF), SQLAlchemy (session isolation) |

### OWASP API Security Top 10 2023

| ID | Category | Requirements |
|----|----------|-------------|
| API1:2023 | Broken Object Level Authorization (BOLA) | CAT-FPI-SEC-001 |
| API2:2023 | Broken Authentication | CAT-FPI-SEC-002 |
| API3:2023 | Broken Object Property Level Authorization (BOPLA) | CAT-FPI-SEC-003, CAT-FPI-API-004 |
| API4:2023 | Unrestricted Resource Consumption | CAT-FPI-SEC-004, CAT-FPI-API-002 |
| API5:2023 | Broken Function Level Authorization (BFLA) | CAT-FPI-SEC-005 |
| API6:2023 | Unrestricted Access to Sensitive Business Flows | CAT-FPI-SEC-006 |
| API7:2023 | Server-Side Request Forgery (SSRF) | CAT-FPI-SEC-007 |
| API8:2023 | Security Misconfiguration | CAT-FPI-SEC-008, CAT-FPI-API-005, CAT-FPI-OBS-005 |
| API9:2023 | Improper Inventory Management | CAT-FPI-SEC-009, CAT-FPI-API-006 |
| API10:2023 | Unsafe Consumption of APIs | CAT-FPI-SEC-010 |

## Coverage Summary

| Catalog | Requirements | With Standards | Standards Count |
|---------|-------------|---------------|-----------------|
| PyTorch Training | 32 | 22 (69%) | 7 frameworks |
| HuggingFace Inference | 25 | 14 (56%) | 5 frameworks |
| FastAPI | 22 | 22 (100%) | 5 frameworks |
| SQLAlchemy | 18 | 10 (56%) | 4 frameworks |
| Pyomo | 19 | 19 (100%) | 8 frameworks |
| **Total** | **116** | **87 (75%)** | **10 frameworks** |

## IEEE 754 Floating-Point Requirements

Four dedicated IEEE 754 requirements were added to address common numerical hazards:

| ID | Catalog | Topic |
|----|---------|-------|
| CAT-PYT-GRAD-007 | PyTorch | Overflow/underflow detection in gradients (IEEE 754 §7.4, §7.5) |
| CAT-PYT-LOSS-007 | PyTorch | Numerically stable loss functions (log-sum-exp, cross-entropy) |
| CAT-HGF-ATTN-007 | HuggingFace | Mixed-precision dtype consistency in attention (IEEE 754 §5.4) |
| CAT-PYO-CVAL-007 | Pyomo | Compensated summation for constraint evaluation (IEEE 754 §9.4) |

## Cross-Cutting Patterns

Several standards apply across multiple catalogs, reflecting common V&V concerns:

- **Configuration Management** (NASA SE 6.5, INCOSE 5.5): Version pinning, checkpoint state, migration tracking — applies to PyTorch, HuggingFace, FastAPI, SQLAlchemy, Pyomo
- **Measurement & Monitoring** (INCOSE 5.7): Gradient norms, solver metrics, API RED metrics, conformance rates — applies to all catalogs
- **Verification Process** (NASA SE 5.3, DO-178C 6.1): Requirements-based testing as the foundation for all catalogs
- **Functional Correctness** (ISO 25010 4.1.2): Numerical correctness, round-trip losslessness, schema conformance — applies to all catalogs
- **Fault Tolerance** (ISO 25010 4.5.3): Retry logic, graceful degradation, adversarial robustness — applies to all catalogs
- **Floating-Point Discipline** (IEEE 754): NaN/Inf handling, overflow/underflow, precision management — applies to PyTorch, HuggingFace, Pyomo
