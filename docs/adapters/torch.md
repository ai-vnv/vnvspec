# PyTorch Adapter

The `vnvspec.torch` module provides adapters that wrap PyTorch and HuggingFace models, implementing the `ModelAdapter` protocol for automated V&V assessment.

## Installation

```bash
pip install vnvspec[torch]
```

This installs `torch>=2.3` and `transformers>=4.40` as additional dependencies.

## TorchAdapter

`TorchAdapter` wraps any `torch.nn.Module` and runs it through a spec's requirements, producing an assessment `Report`.

```python
from vnvspec.torch import TorchAdapter

adapter = TorchAdapter(
    model,
    device="cuda",
    sample_budget=1000,
    batch_size=32,
)
report = adapter.assess(spec, data_loader)
print(report.verdict())
```

**Constructor parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `model` | `nn.Module` | The PyTorch model to assess |
| `input_adapter` | `Any` | Optional callable to preprocess inputs |
| `output_adapter` | `Any` | Optional callable to postprocess outputs |
| `device` | `str` | Device to run on (`"cpu"`, `"cuda"`) |
| `sample_budget` | `int` | Maximum number of samples to evaluate |
| `batch_size` | `int` | Batch size for evaluation (default 32) |

## Specialized Adapters

- **`TransformerAdapter`** -- wraps HuggingFace transformer models with tokenizer integration
- **`AutoregressiveAdapter`** -- handles autoregressive generation with stopping criteria
- **`VLMAdapter`** -- wraps vision-language models with image preprocessing

## Supporting Utilities

- **`HookManager`** -- attach forward/backward hooks to model layers for intermediate activation inspection
- **`SampleBudgetIterator`** -- wraps a DataLoader to enforce a maximum sample budget, stopping iteration once the budget is reached

## ModelAdapter Protocol

All adapters implement the `ModelAdapter` protocol defined in `vnvspec.core.protocols`. Custom adapters for other frameworks (scikit-learn, ONNX, etc.) can implement this same protocol.

**API reference:** `vnvspec.torch.adapter.TorchAdapter`, `vnvspec.torch.hooks.HookManager`, `vnvspec.torch.sampling.SampleBudgetIterator`
