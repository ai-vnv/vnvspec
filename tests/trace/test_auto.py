"""Tests for auto_trace() regex-based traceability."""

from __future__ import annotations

from pathlib import Path

import pytest

from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec
from vnvspec.trace.auto import auto_trace


@pytest.fixture()
def sample_spec() -> Spec:
    return Spec(
        name="trace-test",
        requirements=[
            Requirement(
                id="REQ-001",
                statement="The system shall validate input.",
                rationale="Safety.",
                verification_method="test",
                acceptance_criteria=["Input validated."],
            ),
            Requirement(
                id="REQ-002",
                statement="The system shall log errors.",
                rationale="Observability.",
                verification_method="test",
                acceptance_criteria=["Errors logged."],
            ),
            Requirement(
                id="REQ-003",
                statement="The system shall handle timeouts.",
                rationale="Resilience.",
                verification_method="test",
                acceptance_criteria=["Timeouts handled."],
            ),
        ],
    )


@pytest.fixture()
def fixture_tree(tmp_path: Path) -> Path:
    """Create a fixture project tree with embedded requirement IDs."""
    src = tmp_path / "src"
    src.mkdir()
    tests = tmp_path / "tests"
    tests.mkdir()

    (src / "validator.py").write_text(
        '"""Input validation module."""\n'
        "# Implements REQ-001\n"
        "def validate(data):\n"
        "    # REQ-001: validate all inputs\n"
        "    return True\n"
    )
    (src / "logger.py").write_text(
        '"""Logging module."""\n# REQ-002: error logging\ndef log_error(msg):\n    pass\n'
    )
    (tests / "test_validator.py").write_text(
        "# Tests for REQ-001\ndef test_validate():\n    # Verifies REQ-001\n    assert True\n"
    )
    (tests / "test_logger.py").write_text(
        "# Tests for REQ-002\ndef test_log_error():\n    assert True\n"
    )
    # A file that mentions REQ-001X (near-match, should not match)
    (tests / "test_near_miss.py").write_text(
        "# REQ-001X is not a real requirement\ndef test_nothing():\n    pass\n"
    )
    # Binary-like file (should be skipped)
    (src / "data.bin").write_bytes(b"\x00\x01REQ-001\x02")

    return tmp_path


class TestAutoTrace:
    def test_finds_all_hits(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree])
        req_001_links = [l for l in links if l.source_id == "REQ-001"]
        assert len(req_001_links) >= 3  # validator.py (2 hits) + test_validator.py (2 hits)

    def test_finds_req_002(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree])
        req_002_links = [l for l in links if l.source_id == "REQ-002"]
        assert len(req_002_links) >= 2

    @pytest.mark.vnvspec("REQ-SELF-TRACE-001")
    def test_no_false_positives(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree])
        # REQ-001X should not match (word boundary prevents it)
        all_targets = [l.target_id for l in links]
        near_miss_hits = [t for t in all_targets if "test_near_miss.py" in t]
        # Only if REQ-001 appears after REQ-001X on the same line would it match
        # In our fixture, REQ-001X is the only pattern on that line
        assert len(near_miss_hits) == 0

    def test_no_hits_for_req_003(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree])
        req_003_links = [l for l in links if l.source_id == "REQ-003"]
        assert len(req_003_links) == 0

    def test_deduplication(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree])
        pairs = [(l.source_id, l.target_id) for l in links]
        assert len(pairs) == len(set(pairs))

    def test_relation_type(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree], relation="satisfies")
        for link in links:
            assert link.relation == "satisfies"

    def test_empty_spec(self, fixture_tree: Path) -> None:
        spec = Spec(name="empty")
        links = auto_trace(spec, paths=[fixture_tree])
        assert len(links) == 0

    def test_single_file(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(
            sample_spec,
            paths=[fixture_tree / "src" / "validator.py"],
        )
        assert len(links) >= 2
        assert all(l.source_id == "REQ-001" for l in links)

    def test_metadata_contains_line(self, sample_spec: Spec, fixture_tree: Path) -> None:
        links = auto_trace(sample_spec, paths=[fixture_tree])
        for link in links:
            assert "line" in link.metadata

    def test_extra_patterns(self, sample_spec: Spec, fixture_tree: Path) -> None:
        """Extra user patterns that match known IDs produce TraceLinks."""
        links = auto_trace(sample_spec, paths=[fixture_tree], patterns=[r"REQ-\d+"])
        req_001_links = [l for l in links if l.source_id == "REQ-001"]
        assert len(req_001_links) >= 2

    def test_extra_patterns_unknown_warns(self, tmp_path: Path) -> None:
        """Extra pattern matching an unknown ID emits a warning."""
        spec = Spec(
            name="t",
            requirements=[
                Requirement(
                    id="REQ-001",
                    statement="X.",
                    verification_method="test",
                )
            ],
        )
        (tmp_path / "code.py").write_text("# UNKNOWN-999 here\n")
        with pytest.warns(RuntimeWarning, match="UNKNOWN-999"):
            auto_trace(spec, paths=[tmp_path], patterns=[r"UNKNOWN-\d+"])

    def test_unreadable_file(self, sample_spec: Spec, tmp_path: Path) -> None:
        """Unreadable files are silently skipped."""
        bad = tmp_path / "bad.py"
        bad.write_text("REQ-001 here")
        bad.chmod(0o000)
        try:
            auto_trace(sample_spec, paths=[tmp_path])
            # Should not crash, may or may not find the link depending on OS
        finally:
            bad.chmod(0o644)

    def test_non_text_suffix_skipped(self, sample_spec: Spec, tmp_path: Path) -> None:
        """Files with non-text suffixes are skipped."""
        (tmp_path / "data.xyz").write_text("REQ-001 here")
        links = auto_trace(sample_spec, paths=[tmp_path])
        assert len(links) == 0

    def test_exclude_dirs(self, sample_spec: Spec, fixture_tree: Path) -> None:
        # Create a __pycache__ dir with a matching file
        cache_dir = fixture_tree / "src" / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "cached.py").write_text("# REQ-001 in cache\n")

        links = auto_trace(sample_spec, paths=[fixture_tree])
        cache_hits = [l for l in links if "__pycache__" in l.target_id]
        assert len(cache_hits) == 0
