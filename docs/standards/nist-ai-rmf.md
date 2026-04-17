# NIST AI RMF

**NIST Artificial Intelligence Risk Management Framework**

## Overview

The NIST AI Risk Management Framework (AI RMF 1.0) provides voluntary guidance for managing risks associated with AI systems throughout their lifecycle. It is organized around four core functions -- Govern, Map, Measure, and Manage -- that together form a structured approach to AI risk management.

## Core Functions

- **Govern** -- establish policies, processes, and accountability structures for AI risk management
- **Map** -- contextualize risks by understanding the AI system's purpose, stakeholders, and operating environment
- **Measure** -- employ quantitative and qualitative methods to assess identified risks
- **Manage** -- prioritize and act on risks according to their assessed impact and likelihood

## Key Topics

- **Trustworthy AI characteristics** -- validity, reliability, safety, fairness, transparency, explainability, privacy, and security
- **Risk tiering** -- categorization of AI systems by risk level to allocate management effort
- **Stakeholder engagement** -- involving affected parties in risk identification and evaluation
- **Documentation and reporting** -- maintaining records of risk assessments and mitigation actions

## Relevance to vnvspec

vnvspec's requirement and evidence models map well to the Measure and Manage functions of the AI RMF:

```python
from vnvspec import Requirement

req = Requirement(
    id="REQ-FAIR-001",
    statement="The model shall achieve equalized odds across demographic groups with disparity below 0.05.",
    verification_method="test",
    standards={"nist_ai_rmf": ["MEASURE 2.6", "MANAGE 3.1"]},
)
```

The `coverage_report()` utility helps demonstrate that all identified risks have corresponding verification evidence, supporting the Manage function's documentation requirements.

**See also:** `vnvspec.core.trace.coverage_report` for traceability coverage analysis.
