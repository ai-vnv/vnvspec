# Per-Phase Spec Files

For projects with >30 requirements, a single spec file becomes unwieldy. This recipe shows how to split requirements across multiple files and assemble them into a master spec.

## Layout

```
specs/
├── phase1_data.yaml
├── phase2_model.yaml
├── phase3_api.yaml
├── phase4_auth.yaml
└── master.py          # assembles all phases
```

## Phase file (YAML)

```yaml
# specs/phase1_data.yaml
requirements:
  - id: REQ-DATA-001
    statement: The system shall validate all input data against the schema.
    rationale: Data integrity is required for downstream model accuracy.
    verification_method: test
    acceptance_criteria:
      - Invalid inputs rejected with HTTP 422
```

## Master assembler

```python
# specs/master.py
from pathlib import Path
import yaml
from vnvspec import Spec, Requirement

spec = Spec(name="my-project", version="1.0")

for phase_file in sorted(Path("specs").glob("phase*.yaml")):
    data = yaml.safe_load(phase_file.read_text())
    reqs = [Requirement.model_validate(r) for r in data["requirements"]]
    spec = spec.extend(reqs)

# Or use Spec.from_yaml() for each phase and extend:
# spec = spec.extend(Spec.from_yaml("specs/phase1_data.yaml").requirements)
```

## Benefits

- Each phase owner edits only their file
- Git diffs are scoped to the changed phase
- Review cycles are faster (smaller files)
- The master assembler catches duplicate IDs across phases at build time
