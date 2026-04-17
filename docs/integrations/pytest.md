# pytest Integration

The `pytest-vnvspec` plugin captures V&V evidence directly from pytest test results.

## Installation

```bash
pip install pytest-vnvspec
```

## Usage

### 1. Mark tests with requirement IDs

```python
import pytest

@pytest.mark.vnvspec("REQ-001")
def test_accuracy():
    assert model.accuracy() > 0.9

@pytest.mark.vnvspec("REQ-002")
def test_latency():
    assert model.latency_ms() < 100
```

A test can have multiple markers:

```python
@pytest.mark.vnvspec("REQ-001")
@pytest.mark.vnvspec("REQ-003")
def test_accuracy_and_consistency():
    ...
```

### 2. Run with spec file

```bash
pytest --vnvspec-spec=spec.yaml --vnvspec-report=report.json
```

### 3. Review the report

The report JSON contains evidence for every marked test plus inconclusive evidence for any test-method requirement with no linked test.

## CLI Options

| Option | Description | Default |
|---|---|---|
| `--vnvspec-spec=PATH` | Path to spec file (YAML/TOML/JSON) | None (plugin inactive) |
| `--vnvspec-report=PATH` | Output report path (JSON) | None (no file written) |
| `--vnvspec-fail-on=MODE` | `any`, `blocking`, or `never` | `never` |

## Behavior

- **Collection**: markers referencing unknown requirement IDs produce a `PytestUnknownMarkWarning` but don't break the run.
- **Execution**: each test's pass/fail verdict is captured as `Evidence`.
- **Session end**: requirements with `verification_method="test"` and no matching test get `verdict="inconclusive"`.
- **Fail-on policy**: `any` fails the session if any evidence has `verdict="fail"`. `blocking` only fails on `priority="blocking"` requirements. `never` (default) leaves pytest's normal exit code unchanged.
