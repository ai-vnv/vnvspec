# Spec File Formats

vnvspec supports three formats for defining specifications: **YAML**, **TOML**, and **Python**. Choose the one that best fits your workflow.

## When to use each format

| Format | Best for | Tradeoffs |
|---|---|---|
| **YAML** | Most projects, especially with >30 requirements | Human-readable, easy to diff, but no code execution |
| **TOML** | Config-heavy projects, Rust/Python ecosystem alignment | Strict typing, but verbose for nested structures |
| **Python** | Small specs, programmatic generation, computed values | Full language power, but harder to review as a "document" |

## YAML

```yaml
name: my-system
version: "1.0"
requirements:
  - id: REQ-001
    statement: The system shall respond within 100 ms.
    rationale: Latency budget from architecture.
    verification_method: test
    acceptance_criteria:
      - p99 latency < 100 ms
```

```python
from vnvspec import Spec

spec = Spec.from_yaml("spec.yaml")
spec.to_yaml("spec-out.yaml")  # round-trips cleanly
```

## TOML

```toml
name = "my-system"
version = "1.0"

[[requirements]]
id = "REQ-001"
statement = "The system shall respond within 100 ms."
rationale = "Latency budget from architecture."
verification_method = "test"
acceptance_criteria = ["p99 latency < 100 ms"]
```

```python
spec = Spec.from_toml("spec.toml")
spec.to_toml("spec-out.toml")
```

## Python

```python
from vnvspec import Requirement, Spec

spec = Spec(
    name="my-system",
    version="1.0",
    requirements=[
        Requirement(
            id="REQ-001",
            statement="The system shall respond within 100 ms.",
            rationale="Latency budget from architecture.",
            verification_method="test",
            acceptance_criteria=["p99 latency < 100 ms"],
        ),
    ],
)
```

## Scaffolding

Use the CLI to scaffold a spec in your preferred format:

```bash
vnvspec init --format yaml   # default
vnvspec init --format toml
vnvspec init --format py
```

## Round-trip guarantee

The YAML and TOML shapes are exactly the JSON shape Pydantic produces — no custom translation. This means:

- `Spec.from_yaml(spec.to_yaml())` produces an identical Spec
- `Spec.from_toml(spec.to_toml())` produces an identical Spec
- You can hand-edit either format and load it back
