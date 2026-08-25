"""ISO/IEC 42001 Artificial Intelligence Management System (AIMS) catalog.

This catalog provides reusable governance and management requirements for
organizations establishing an AI Management System (AIMS) in accordance with
ISO/IEC 42001:2023.

It is a baseline, not a substitute for expert review.

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Last reviewed: 2026-07-26
"""

from vnvspec.catalog.standards.iso_42001.annex_a_controls import annex_a_controls
from vnvspec.catalog.standards.iso_42001.management_controls import management_controls

__all__ = [
    "annex_a_controls",
    "management_controls",
]
