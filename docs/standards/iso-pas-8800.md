# ISO/PAS 8800

**Road vehicles -- Safety and artificial intelligence**

## Overview

ISO/PAS 8800 is a publicly available specification that provides guidance on the safety-related aspects of AI used in road vehicles. It extends the ISO 26262 functional safety framework to address the unique challenges of machine learning components, such as data quality, model robustness, and operational design domain specification.

## Key Topics

- **Data quality and management** -- requirements for training, validation, and test data
- **Model verification** -- techniques for verifying ML model behavior, including robustness testing and coverage metrics
- **Operational Design Domain (ODD)** -- formal specification of conditions under which the AI system is designed to operate
- **Uncertainty estimation** -- approaches for quantifying and managing model uncertainty
- **Continuous learning** -- guidance on systems that update after deployment

## Relevance to vnvspec

vnvspec's `Requirement.standards` field accepts `"iso_pas_8800"` as a key, allowing you to trace requirements to specific clauses:

```python
from vnvspec import Requirement

req = Requirement(
    id="REQ-DATA-001",
    statement="The training dataset shall have documented provenance for all samples.",
    verification_method="inspection",
    standards={"iso_pas_8800": ["6.2.1", "6.2.3"]},
)
```

The built-in standards registry provides clause metadata for ISO/PAS 8800, enabling automated traceability reports and gap analysis.

**See also:** `vnvspec.registries` for the clause database.
