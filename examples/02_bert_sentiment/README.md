# Example 02 — BERT Sentiment Classification

Uses `TransformerAdapter` with `prajjwal1/bert-tiny` to run a vnvspec
assessment on a small sentiment-classification task.

## Prerequisites

```bash
pip install vnvspec[torch]
```

The script downloads `prajjwal1/bert-tiny` (~17 MB) on the first run.

## Run

```bash
python main.py
```

The script will:

1. Load BERT-tiny for sequence classification via `TransformerAdapter`.
2. Define three requirements (output shape, probability range, latency).
3. Run `assess()` on a handful of sample sentences.
4. Export the report as `report.html` and print a summary to stdout.
