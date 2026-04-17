# IO Contract

The `IOContract` class defines the expected input schema, output schema, and invariants for a system interface. It is the formal specification of what a component accepts and produces.

## Purpose

IO contracts make interface expectations explicit and machine-checkable. Rather than relying on documentation that drifts from the code, an `IOContract` can be validated at runtime against actual model inputs and outputs.

## Invariant

An `Invariant` is a named condition that must hold for a contract. Each invariant has:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Short invariant name |
| `description` | `str` | Human-readable description |
| `check_expr` | `str` | Python expression with `value` as the variable |

The `check(value)` method evaluates the expression and returns `True` or `False`.

## IOContract Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Contract name |
| `inputs` | `dict[str, Any]` | Input schema as a dict |
| `outputs` | `dict[str, Any]` | Output schema as a dict |
| `invariants` | `list[Invariant]` | Conditions that must hold |

## Checking Invariants

Use `check_invariants(values)` to evaluate all invariants against a dict of named values:

```python
from vnvspec import Invariant, IOContract

inv = Invariant(
    name="probability_range",
    description="Output probability in [0, 1]",
    check_expr="0 <= value <= 1",
)

contract = IOContract(
    name="classifier-io",
    inputs={"image": {"type": "tensor", "shape": [3, 224, 224]}},
    outputs={"probability": {"type": "float", "range": [0.0, 1.0]}},
    invariants=[inv],
)

results = contract.check_invariants({"probability_range": 0.85})
print(results)  # {'probability_range': True}
```

## Integration with Spec

IO contracts are attached to a `Spec` via the `contracts` field and can be used by adapters during assessment to verify that model outputs satisfy interface constraints.

**API reference:** `vnvspec.core.contract.IOContract`, `vnvspec.core.contract.Invariant`
