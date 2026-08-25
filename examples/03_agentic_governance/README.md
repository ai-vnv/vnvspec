# Example 03 — Agentic AI Governance Catalog

Composes the four **Agentic Governance** catalog areas into a single reusable
`Spec` and exports it to YAML. Unlike examples 01 and 02, this example needs no
model, no GPU, and no network access — the governance catalog is offline and
deterministic.

## Prerequisites

```bash
pip install vnvspec
```

## Run

```bash
python main.py
```

The script will:

1. Create a base `Spec` for a customer-support agent.
2. Compose Tool Governance, External Information Governance, Human Oversight,
   and Memory Governance via `Spec.extend()`.
3. Print a summary (total requirements, counts by area and priority).
4. Export the composed spec to `agentic-governance-spec.yaml`.

These are **reusable governance requirements** — a baseline to adopt and adapt,
not a compliance certification.
