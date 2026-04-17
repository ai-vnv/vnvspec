"""vnvspec — V&V-grade specifications for engineered systems."""

from vnvspec._version import __version__
from vnvspec.core.contract import Invariant, IOContract
from vnvspec.core.errors import (
    AssessmentError,
    ContractError,
    RequirementError,
    SpecError,
    VnvspecError,
)
from vnvspec.core.evidence import Evidence
from vnvspec.core.hazard import Hazard
from vnvspec.core.odd import ODD
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.core.trace import TraceLink, build_trace_graph, coverage_report

__all__ = [
    "ODD",
    "AssessmentError",
    "ContractError",
    "Evidence",
    "Hazard",
    "IOContract",
    "Invariant",
    "Requirement",
    "RequirementError",
    "Spec",
    "SpecError",
    "TraceLink",
    "VnvspecError",
    "__version__",
    "build_trace_graph",
    "coverage_report",
]
