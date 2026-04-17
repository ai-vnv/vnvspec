"""BERT Sentiment — vnvspec TransformerAdapter example.

Loads prajjwal1/bert-tiny via TransformerAdapter, defines a Spec
with 3 requirements, runs assess(), and exports an HTML report.

Usage:
    python main.py
"""

from __future__ import annotations

from pathlib import Path

from vnvspec import Requirement, Spec
from vnvspec.exporters.html import export_html
from vnvspec.torch import TransformerAdapter

# ── 1. Define the Spec ──────────────────────────────────────────────

spec = Spec(
    name="bert-sentiment-spec",
    version="0.1.0",
    description="V&V spec for a tiny BERT sentiment classifier.",
    requirements=[
        Requirement(
            id="REQ-SHAPE",
            statement="The model shall output a tensor of shape (batch, num_labels).",
            rationale="Output dimensions must match the label space.",
            verification_method="test",
            acceptance_criteria=["Output has 2 columns (pos/neg)."],
        ),
        Requirement(
            id="REQ-PROB",
            statement="The model shall produce valid probabilities summing to 1.",
            rationale="Softmax outputs represent a probability distribution.",
            verification_method="test",
            acceptance_criteria=["Row sums equal 1 within tolerance 1e-5."],
        ),
        Requirement(
            id="REQ-NOCRASH",
            statement="The model shall handle inputs up to 512 tokens without error.",
            rationale="Maximum sequence length is a deployment constraint.",
            verification_method="test",
            acceptance_criteria=["No runtime errors on long inputs."],
        ),
    ],
)

# ── 2. Load BERT-tiny with TransformerAdapter ───────────────────────

adapter = TransformerAdapter(
    "prajjwal1/bert-tiny",
    task="text-classification",
    max_length=128,
    batch_size=4,
)

# ── 3. Sample sentences ─────────────────────────────────────────────

sentences = [
    "I absolutely loved this movie, it was fantastic!",
    "Terrible experience, would not recommend.",
    "The product is okay, nothing special.",
    "Best purchase I have ever made.",
    "Waste of money, broke after one day.",
    "Solid quality and fast shipping.",
]

# ── 4. Run assessment ──────────────────────────────────────────────

report = adapter.assess(spec, sentences)

# ── 5. Export HTML and print summary ────────────────────────────────

out_path = Path(__file__).parent / "report.html"
export_html(report, path=out_path)

print(f"Spec:      {report.spec_name} v{report.spec_version}")
print(f"Verdict:   {report.verdict()}")
print(f"Passed:    {report.pass_count()}/{len(report.evidence)}")
print(f"Report:    {out_path}")
