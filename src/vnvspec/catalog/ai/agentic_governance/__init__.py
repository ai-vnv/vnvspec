"""Agentic AI governance catalog — reusable governance requirements for agents.

This catalog reflects published governance guidance for autonomous and
semi-autonomous AI agents as of 2026-07-13.
It is a baseline, not a substitute for expert review.

These requirements are implementation-agnostic and complement, rather than
replace, existing governance frameworks (EU AI Act, NIST AI RMF, GDPR/HIPAA,
and OWASP guidance for LLM applications).

Last reviewed: 2026-07-13
"""

from vnvspec.catalog.ai.agentic_governance.external_information_governance import (
    external_information_governance,
)
from vnvspec.catalog.ai.agentic_governance.human_oversight import human_oversight
from vnvspec.catalog.ai.agentic_governance.memory_governance import memory_governance
from vnvspec.catalog.ai.agentic_governance.tool_governance import tool_governance

__all__ = [
    "external_information_governance",
    "human_oversight",
    "memory_governance",
    "tool_governance",
]
