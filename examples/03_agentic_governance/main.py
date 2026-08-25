"""Agentic AI Governance — vnvspec catalog usage example.

Composes the four Agentic Governance catalog areas (Tool Governance,
External Information Governance, Human Oversight, and Memory Governance)
into a single reusable Spec via Spec.extend(), prints a summary, and
exports the composed spec to YAML.

Unlike examples 01 and 02, this example needs no model, no GPU, and no
network access: the governance catalog is offline and deterministic.

Usage:
    python main.py
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from vnvspec import Spec
from vnvspec.catalog.ai.agentic_governance import (
    external_information_governance,
    human_oversight,
    memory_governance,
    tool_governance,
)

# ── 1. Start from a base spec for a specific agent deployment ────────

spec = Spec(
    name="customer-support-agent-governance",
    version="0.1.0",
    description=(
        "Governance baseline for an autonomous customer-support agent, "
        "composed from the vnvspec Agentic Governance catalog."
    ),
)

# ── 2. Compose the four governance areas via Spec.extend() ──────────
# Each catalog function returns list[Requirement]; extend() returns a
# new frozen Spec (the original is never mutated).

spec = spec.extend(
    tool_governance(),
    external_information_governance(),
    human_oversight(),
    memory_governance(),
)

# ── 3. Summarize the composed governance spec ───────────────────────
# Area is the third CAT-ID segment, e.g. CAT-AGT-TOOL-001 -> "TOOL".

by_area = Counter(req.id.split("-")[2] for req in spec.requirements)
by_priority = Counter(req.priority for req in spec.requirements)

print(f"Spec:        {spec.name} v{spec.version}")
print(f"Total reqs:  {len(spec.requirements)}")
print(f"By area:     {dict(by_area)}")
print(f"By priority: {dict(by_priority)}")

# ── 4. Export the composed spec as a reusable YAML artifact ─────────

out_path = Path(__file__).parent / "agentic-governance-spec.yaml"
spec.to_yaml(path=out_path)
print(f"Spec YAML:   {out_path}")
