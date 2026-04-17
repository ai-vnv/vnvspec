# EU AI Act

**Regulation (EU) on Artificial Intelligence**

## Overview

The EU AI Act is the European Union's comprehensive regulation for artificial intelligence. It establishes a risk-based classification system for AI systems, with the most stringent requirements applying to high-risk applications such as safety components of regulated products, biometric identification, and critical infrastructure.

## Key Topics

- **Risk classification** -- minimal, limited, high, and unacceptable risk categories
- **High-risk requirements** -- risk management, data governance, technical documentation, transparency, human oversight, accuracy, robustness, and cybersecurity
- **Annex IV technical documentation** -- detailed documentation requirements for high-risk AI systems
- **Conformity assessment** -- procedures for demonstrating compliance before placing a system on the market
- **Post-market monitoring** -- ongoing obligations for deployed high-risk systems

## Relevance to vnvspec

vnvspec includes a dedicated Annex IV technical documentation exporter (`vnvspec.exporters.techdoc_annex_iv`) that generates the required documentation structure from a spec:

```python
from vnvspec import Requirement

req = Requirement(
    id="REQ-TRANS-001",
    statement="The system shall provide human-readable explanations for all classification decisions.",
    verification_method="demonstration",
    standards={"eu_ai_act": ["Art. 13", "Annex IV.2"]},
)
```

The `Evidence` model's `artifact_uri` field supports linking to test reports and compliance artifacts required by the Act's documentation obligations.

**See also:** `vnvspec.exporters.techdoc_annex_iv` for Annex IV document generation.
