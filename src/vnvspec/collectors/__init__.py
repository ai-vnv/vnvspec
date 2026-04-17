"""Evidence collection utilities.

The :class:`EvidenceCollector` context manager provides an ergonomic API
for building :class:`~vnvspec.core.evidence.Evidence` objects from inline
assertions and external test results (e.g. JUnit XML).
"""

from vnvspec.collectors.evidence import EvidenceCollector

__all__ = ["EvidenceCollector"]
