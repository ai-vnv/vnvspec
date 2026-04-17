"""Tabular MLP — vnvspec quick-start example.

Creates a 3-layer MLP, defines a Spec with 3 requirements,
wraps the model with TorchAdapter, runs assess(), and exports
the report as HTML.

Usage:
    python main.py
"""

from __future__ import annotations

from pathlib import Path

import torch
from torch import nn

from vnvspec import Requirement, Spec
from vnvspec.exporters.html import export_html
from vnvspec.torch import TorchAdapter

# ── 1. Define a simple 3-layer MLP ──────────────────────────────────


class TabularMLP(nn.Module):
    def __init__(self, in_dim: int = 10, out_dim: int = 3) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, out_dim),
            nn.Softmax(dim=-1),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


# ── 2. Define a Spec with 3 requirements ────────────────────────────

spec = Spec(
    name="tabular-mlp-spec",
    version="0.1.0",
    description="V&V spec for a simple tabular classifier.",
    requirements=[
        Requirement(
            id="REQ-PROB",
            statement="The model shall output probabilities in [0, 1].",
            rationale="Outputs represent class probabilities.",
            verification_method="test",
            acceptance_criteria=["All output values >= 0 and <= 1."],
        ),
        Requirement(
            id="REQ-DIM",
            statement="The model shall produce exactly 3 output dimensions.",
            rationale="There are 3 target classes.",
            verification_method="test",
            acceptance_criteria=["Output tensor has shape (batch, 3)."],
        ),
        Requirement(
            id="REQ-NAN",
            statement="The model shall not produce NaN values.",
            rationale="NaN outputs indicate numerical instability.",
            verification_method="test",
            acceptance_criteria=["No NaN values in output tensor."],
        ),
    ],
)

# ── 3. Wrap with TorchAdapter ───────────────────────────────────────

model = TabularMLP(in_dim=10, out_dim=3)
adapter = TorchAdapter(model, batch_size=64)

# ── 4. Generate random data and run assessment ──────────────────────

data = [torch.randn(10) for _ in range(200)]
report = adapter.assess(spec, data)

# ── 5. Export HTML and print summary ────────────────────────────────

out_path = Path(__file__).parent / "report.html"
export_html(report, path=out_path)

print(f"Spec:      {report.spec_name} v{report.spec_version}")
print(f"Verdict:   {report.verdict()}")
print(f"Passed:    {report.pass_count()}/{len(report.evidence)}")
print(f"Report:    {out_path}")
