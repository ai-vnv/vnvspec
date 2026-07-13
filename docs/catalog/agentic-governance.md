# Agentic AI Governance Catalog

The Agentic Governance catalog ships pre-written, reusable `Requirement` objects
for the governance of autonomous and semi-autonomous AI agents — systems that
pursue goals over multiple steps and may invoke tools, consume external
information, act under human oversight, or retain persistent memory.

!!! note "Reusable requirements, not a standard"
    This is a **catalog of reusable governance requirements**, not a standard or
    a compliance certification. The requirements are *informed by* and *aligned
    with* public guidance (EU AI Act, NIST AI RMF, OWASP guidance for LLM
    applications, and GDPR); they **complement** those frameworks rather than
    replace them, and they make no claim of compliance. Treat the catalog as a
    baseline, not a substitute for expert review.

## Purpose

Teams deploying AI agents repeatedly re-author the same governance requirements
— "require approval before irreversible actions", "isolate memory between
users", "validate tool outputs" — inconsistently and without traceability. This
catalog provides those requirements once, as GtWR-clean, standards-mapped,
stably-identified `Requirement` objects that compose into any `Spec`.

## Scope

The catalog covers four governance areas:

| Area | Module | Governs |
|------|--------|---------|
| Tool Governance | `tool_governance` | Which actions the agent may take through tools, and how high-consequence actions are authorized, gated, validated, and recorded. |
| External Information Governance | `external_information_governance` | How externally sourced content is bounded — kept as untrusted data, separated from operator instructions, and admitted only from verified sources. |
| Human Oversight | `human_oversight` | Effective, meaningful human control — halting, approval, escalation, override, accountability, and preservation of human authority. |
| Memory Governance | `memory_governance` | How persisted agent memory is scoped, isolated, retained, deleted, and made traceable. |

Planning Governance and Multi-Agent Governance are intentionally out of scope for
this version.

## Intended use

Adopt the catalog as a starting baseline for an agent deployment's specification,
then adapt it to the deployment's context: keep the requirements that apply,
tighten acceptance criteria to local policy, and add domain-specific
requirements alongside. Because the entries are ordinary `Requirement` objects,
they gain traceability, GtWR quality checking, standards gap analysis, and
serialization for free.

## How the four areas relate

The areas form complementary boundaries around an agent's autonomy:

- **Tool Governance** bounds what the agent can *do*.
- **External Information Governance** bounds what the agent can *trust and act on*.
- **Human Oversight** keeps a person *in control* of that autonomy.
- **Memory Governance** bounds what the agent may *retain* across interactions.

Each requirement governs a distinct outcome, and several deliberately reinforce
one another across areas — for example, tool-level and decision-level approval
gates, or instruction-integrity and oversight-integrity controls.

## Relationship with existing frameworks

Every requirement cites the public guidance it is *informed by* — never
"compliant with":

- **EU AI Act** — human oversight, record-keeping, accuracy/robustness, and data governance articles.
- **NIST AI RMF** — the GOVERN, MAP, MEASURE, and MANAGE functions.
- **OWASP guidance for LLM applications** — excessive agency, prompt injection, and improper output handling.
- **GDPR** — purpose and storage limitation, erasure, and security of processing.

Standards mappings use registry-consistent keys (`eu_ai_act`, `nist_ai_rmf`) so
they line up with `standard_gap_analysis()`; `owasp_llm` and `gdpr` are
documentary keys.

## Usage

Each area is a pure function returning `list[Requirement]`. Compose them into a
spec with `Spec.extend()`:

```python
from vnvspec import Spec
from vnvspec.catalog.ai.agentic_governance import (
    tool_governance,
    external_information_governance,
    human_oversight,
    memory_governance,
)

spec = Spec(name="my-agent-governance")
spec = spec.extend(
    tool_governance(),
    external_information_governance(),
    human_oversight(),
    memory_governance(),
)
```

`Spec.extend()` returns a new frozen `Spec` — the original is never mutated.

Requirement IDs follow the `CAT-AGT-<AREA>-<NNN>` convention (`TOOL`, `INFO`,
`HUM`, `MEM`) and are stable — they are deprecated, never renumbered. The catalog
is discovered automatically by `vnvspec catalog list` and validated against the
inclusion policy in `CONTRIBUTING-CATALOG.md`.

See `examples/03_agentic_governance/` for a runnable example.
