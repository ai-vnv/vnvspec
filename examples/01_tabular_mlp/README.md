# Example 01 — Tabular MLP

A minimal example that creates a 3-layer MLP with PyTorch, defines a
vnvspec `Spec` with three requirements, and runs an assessment.

## Prerequisites

```bash
pip install vnvspec[torch]
```

## Run

```bash
python main.py
```

The script will:

1. Build a simple MLP (10 -> 32 -> 16 -> 3).
2. Define three requirements: probability range, output dimension, and no-NaN.
3. Wrap the model with `TorchAdapter`.
4. Run `assess()` on 200 random samples.
5. Export the report as `report.html` and print a summary to stdout.
