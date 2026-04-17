# pytest-vnvspec

A pytest plugin for [vnvspec](https://github.com/ai-vnv/vnvspec) that captures V&V evidence from test results.

## Installation

```bash
pip install pytest-vnvspec
```

## Usage

Mark tests with `@pytest.mark.vnvspec("REQ-001")` to link them to requirements:

```python
import pytest

@pytest.mark.vnvspec("REQ-001")
def test_accuracy():
    assert model.accuracy() > 0.9

@pytest.mark.vnvspec("REQ-002")
def test_latency():
    assert model.latency() < 100
```

Run pytest with the spec file:

```bash
pytest --vnvspec-spec=spec.yaml --vnvspec-report=report.json
```

## Options

- `--vnvspec-spec=PATH` — Path to the spec file (YAML, TOML, or JSON)
- `--vnvspec-report=PATH` — Output path for the assessment report (JSON)
- `--vnvspec-fail-on={any,blocking,never}` — When to fail the test session based on V&V results

## License

Apache-2.0
