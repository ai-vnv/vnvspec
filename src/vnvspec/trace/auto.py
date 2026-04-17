"""auto_trace — scan a project tree for requirement-ID patterns.

Produces :class:`~vnvspec.core.trace.TraceLink` objects automatically by
matching requirement IDs from the spec against source files.
"""

from __future__ import annotations

import re
import warnings
from collections.abc import Sequence
from pathlib import Path

from vnvspec.core.spec import Spec
from vnvspec.core.trace import Relation, TraceLink

_DEFAULT_EXCLUDE = (".git", "node_modules", ".venv", "__pycache__", ".tox", ".mypy_cache")


def auto_trace(
    spec: Spec,
    *,
    paths: Sequence[Path | str],
    patterns: Sequence[str] | None = None,
    relation: Relation = "verifies",
    exclude: Sequence[str] = _DEFAULT_EXCLUDE,
) -> list[TraceLink]:
    """Scan files for requirement-ID patterns and produce TraceLinks.

    Parameters
    ----------
    spec:
        The spec whose requirement IDs to search for.
    paths:
        Directories and/or files to scan.
    patterns:
        Additional regex patterns to search for (added to auto-derived patterns).
        If ``None``, only patterns derived from ``spec.requirements`` are used.
    relation:
        The relation type for generated links (default: ``"verifies"``).
    exclude:
        Directory names to skip during traversal.

    Returns
    -------
    list[TraceLink]
        Deduplicated trace links. Each link's ``source_id`` is the requirement ID
        and ``target_id`` is ``"<file>:<line>"``.
    """
    req_ids = {r.id for r in spec.requirements}
    if not req_ids:
        return []

    # Build regex from requirement IDs (escape special chars)
    escaped = [re.escape(rid) for rid in sorted(req_ids)]
    id_pattern = re.compile(r"\b(" + "|".join(escaped) + r")\b")

    # Compile additional user patterns
    extra_patterns: list[re.Pattern[str]] = []
    if patterns:
        for p in patterns:
            extra_patterns.append(re.compile(p))

    # Collect files
    files = _collect_files(paths, exclude=set(exclude))

    # Scan files
    seen: set[tuple[str, str]] = set()
    links: list[TraceLink] = []

    for file_path in files:
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            continue

        for line_no, line in enumerate(content.splitlines(), 1):
            # Match spec requirement IDs
            for match in id_pattern.finditer(line):
                req_id = match.group(1)
                target = f"{file_path}:{line_no}"
                key = (req_id, target)
                if key not in seen:
                    seen.add(key)
                    links.append(
                        TraceLink(
                            source_id=req_id,
                            target_id=target,
                            relation=relation,
                            metadata={"line": line.strip()},
                        )
                    )

            # Match extra patterns
            for pat in extra_patterns:
                for match in pat.finditer(line):
                    matched_id = match.group(0)
                    if matched_id not in req_ids:
                        warnings.warn(
                            f"Pattern matched '{matched_id}' at {file_path}:{line_no} "
                            f"but it is not a known requirement ID — skipping.",
                            RuntimeWarning,
                            stacklevel=2,
                        )
                        continue
                    target = f"{file_path}:{line_no}"
                    key = (matched_id, target)
                    if key not in seen:
                        seen.add(key)
                        links.append(
                            TraceLink(
                                source_id=matched_id,
                                target_id=target,
                                relation=relation,
                                metadata={"line": line.strip()},
                            )
                        )

    return links


def _collect_files(
    paths: Sequence[Path | str],
    *,
    exclude: set[str],
) -> list[Path]:
    """Recursively collect files from given paths, skipping excluded dirs."""
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and not any(part in exclude for part in child.parts):
                    # Skip binary-looking files
                    if child.suffix in (
                        ".py",
                        ".txt",
                        ".md",
                        ".rst",
                        ".yaml",
                        ".yml",
                        ".toml",
                        ".json",
                        ".cfg",
                        ".ini",
                        ".sh",
                        ".ts",
                        ".js",
                        ".java",
                        ".go",
                        ".rs",
                        ".c",
                        ".cpp",
                        ".h",
                    ):
                        files.append(child)
    return files
