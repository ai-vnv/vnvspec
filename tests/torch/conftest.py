"""Shared fixtures for torch adapter tests.

Heavy dependencies (torch, transformers) are imported inside fixture
bodies so this conftest remains importable in environments without the
``[torch]`` extra (e.g. for tests/torch/test_sampling.py).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec

# Minimal WordPiece vocabulary for the tiny offline BERT tokenizer.
_TINY_VOCAB = [
    "[PAD]",
    "[UNK]",
    "[CLS]",
    "[SEP]",
    "[MASK]",
    "the",
    "a",
    "test",
    "hello",
    "world",
    "this",
    "is",
    "of",
    "and",
    "input",
    "model",
    "##s",
    "##ing",
    ".",
    ",",
    "!",
]


@pytest.fixture(scope="session")
def tiny_bert_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a tiny random-weight BERT classifier on disk, fully offline.

    Mirrors the local-model pattern of tests/torch/test_adapter.py
    (SimpleMLP): a real model constructed locally, no network access.
    """
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers import BertConfig, BertForSequenceClassification, BertTokenizer

    model_dir = tmp_path_factory.mktemp("tiny-bert")
    vocab_file = model_dir / "vocab.txt"
    vocab_file.write_text("\n".join(_TINY_VOCAB) + "\n", encoding="utf-8")

    config = BertConfig(
        vocab_size=len(_TINY_VOCAB),
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=32,
        max_position_embeddings=512,
        num_labels=2,
        pad_token_id=0,
    )
    # Fork the RNG so the deterministic seed does not leak into the
    # process-global generator seen by other tests.
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(0)
        model = BertForSequenceClassification(config)
    model.save_pretrained(model_dir)
    BertTokenizer(str(vocab_file)).save_pretrained(model_dir)
    return model_dir


# Minimal byte-level BPE artifacts for the tiny offline GPT-2 tokenizer.
# The merges join "hello" and " world" into single tokens; other text over
# the alphabet {h, e, l, o, w, r, d, space} tokenizes character by character,
# and only characters outside that alphabet map to <unk>.
_TINY_GPT2_VOCAB = [
    "<unk>",
    "<|endoftext|>",
    "h",
    "e",
    "l",
    "o",
    "w",
    "r",
    "d",
    "Ġ",  # byte-level BPE space marker (Ġ)
    "he",
    "ll",
    "hell",
    "hello",
    "Ġw",
    "Ġwo",
    "Ġwor",
    "Ġworl",
    "Ġworld",
]
_TINY_GPT2_MERGES = [
    "#version: 0.2",
    "h e",
    "l l",
    "he ll",
    "hell o",
    "Ġ w",
    "Ġw o",
    "Ġwo r",
    "Ġwor l",
    "Ġworl d",
]


@pytest.fixture(scope="session")
def tiny_gpt2_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build a tiny random-weight GPT-2 causal LM on disk, fully offline.

    The saved tokenizer has no pad token (like real GPT-2), which
    exercises the adapter's pad-token defaulting branch on load.
    """
    torch = pytest.importorskip("torch")
    pytest.importorskip("transformers")
    from transformers import GPT2Config, GPT2LMHeadModel, GPT2Tokenizer

    model_dir = tmp_path_factory.mktemp("tiny-gpt2")
    vocab_file = model_dir / "vocab.json"
    merges_file = model_dir / "merges.txt"
    vocab_file.write_text(
        json.dumps({tok: i for i, tok in enumerate(_TINY_GPT2_VOCAB)}), encoding="utf-8"
    )
    merges_file.write_text("\n".join(_TINY_GPT2_MERGES) + "\n", encoding="utf-8")

    config = GPT2Config(
        vocab_size=len(_TINY_GPT2_VOCAB),
        n_positions=64,
        n_embd=16,
        n_layer=1,
        n_head=2,
        bos_token_id=1,
        eos_token_id=1,
    )
    # Fork the RNG so the deterministic seed does not leak into the
    # process-global generator seen by other tests.
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(0)
        model = GPT2LMHeadModel(config)
    model.save_pretrained(model_dir)
    GPT2Tokenizer(str(vocab_file), str(merges_file), unk_token="<unk>").save_pretrained(model_dir)
    return model_dir


@pytest.fixture()
def transformers_module() -> Any:
    """Return the live transformers module for monkeypatching.

    transformers 5.x replaces its entry in sys.modules during the first
    full ``from_pretrained`` load, so a module object imported when a
    test module was first loaded can go stale. Patches must target the
    object that the adapters' own ``from transformers import ...`` will
    resolve at call time.
    """
    import transformers as current

    return current


@pytest.fixture()
def adapter_spec() -> Spec:
    """Spec with one verifiable requirement and one without acceptance criteria.

    The criteria-less requirement drives the inconclusive branch of the
    adapters' default requirement evaluation.
    """
    return Spec(
        name="adapter-offline-spec",
        requirements=[
            Requirement(
                id="REQ-PROB",
                statement="The model shall produce probabilities in [0, 1].",
                rationale="Valid probability outputs.",
                verification_method="test",
                acceptance_criteria=["All output probabilities are within [0, 1]."],
            ),
            Requirement(
                id="REQ-NOCRIT",
                statement="The model shall satisfy an unstated criterion.",
                rationale="Requirement without acceptance criteria.",
                verification_method="test",
            ),
        ],
    )
