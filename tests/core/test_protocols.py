"""Tests for pluggability protocols."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from vnvspec.core.evidence import Evidence
from vnvspec.core.protocols import Exporter, ModelAdapter, TestRunner


class DummyAdapter:
    """A minimal ModelAdapter implementation for testing."""

    def forward(self, inputs: Any, *, ctx: Any = None) -> Any:
        return inputs

    def describe(self) -> dict[str, Any]:
        return {"name": "dummy"}

    def input_schema(self) -> dict[str, Any] | None:
        return None

    def output_schema(self) -> dict[str, Any] | None:
        return None

    def batch_size_hint(self) -> int:
        return 32

    def supports_streaming(self) -> bool:
        return False


class DummyRunner:
    """A minimal TestRunner implementation for testing."""

    def run(
        self,
        spec: Any,
        adapter: ModelAdapter,
        data: Any,
    ) -> list[Evidence]:
        return [
            Evidence(
                id="EV-dummy",
                requirement_id="REQ-001",
                kind="test",
                verdict="pass",
            )
        ]


class DummyExporter:
    """A minimal Exporter implementation for testing."""

    def export(self, report: Any, path: Path, **kwargs: Any) -> Path:
        path.write_text("exported")
        return path


class NotAnAdapter:
    """Intentionally does not implement ModelAdapter."""

    def hello(self) -> str:
        return "world"


class TestModelAdapterProtocol:
    def test_dummy_satisfies_protocol(self) -> None:
        adapter = DummyAdapter()
        assert isinstance(adapter, ModelAdapter)

    def test_non_adapter_fails(self) -> None:
        obj = NotAnAdapter()
        assert not isinstance(obj, ModelAdapter)

    def test_forward_works(self) -> None:
        adapter = DummyAdapter()
        result = adapter.forward([1, 2, 3])
        assert result == [1, 2, 3]

    def test_describe(self) -> None:
        adapter = DummyAdapter()
        desc = adapter.describe()
        assert desc["name"] == "dummy"


class TestTestRunnerProtocol:
    def test_dummy_satisfies_protocol(self) -> None:
        runner = DummyRunner()
        assert isinstance(runner, TestRunner)

    def test_object_fails(self) -> None:
        assert not isinstance(object(), TestRunner)

    def test_run_returns_evidence(self) -> None:
        runner = DummyRunner()
        adapter = DummyAdapter()
        evidence = runner.run(None, adapter, None)
        assert len(evidence) == 1
        assert evidence[0].verdict == "pass"


class TestExporterProtocol:
    def test_dummy_satisfies_protocol(self) -> None:
        exporter = DummyExporter()
        assert isinstance(exporter, Exporter)

    def test_object_fails(self) -> None:
        assert not isinstance(object(), Exporter)

    def test_export_creates_file(self, tmp_path: Path) -> None:
        exporter = DummyExporter()
        out = exporter.export(None, tmp_path / "report.txt")
        assert out.exists()
