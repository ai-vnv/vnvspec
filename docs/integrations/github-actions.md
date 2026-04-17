# GitHub Actions Integration

vnvspec provides a composite GitHub Action for CI/CD pipelines.

## Quick Start

```yaml
# .github/workflows/vnvspec.yml
name: V&V Assessment
on: [push, pull_request]

jobs:
  vnvspec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ai-vnv/vnvspec/actions/vnvspec@main
        with:
          spec: spec.yaml
          report-format: html,json
          fail-on: any
```

## Inputs

| Input | Description | Required | Default |
|---|---|---|---|
| `spec` | Path to spec file | Yes | — |
| `report-format` | Comma-separated formats | No | `html,json` |
| `fail-on` | `any`, `blocking`, `never` | No | `any` |
| `python-version` | Python version | No | `3.11` |
| `comment-pr` | Post results as PR comment | No | `false` |

## Artifacts

The action uploads these artifacts:

- `vnvspec-report.*` — Assessment reports in requested formats
- `vnvspec-badge.svg` — V&V status badge

## Badge in README

After the action runs, reference the badge from your README:

```markdown
![V&V Status](vnvspec-badge.svg)
```

Or use the badge exporter locally:

```python
from vnvspec.exporters.badge import export_badge
export_badge(report, path="vnvspec-badge.svg")
```
