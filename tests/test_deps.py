"""Test that all runtime imports are declared in pyproject.toml dependencies.

Prevents the class of bug where tests pass (dev deps installed) but
`pip install vnvspec` fails with ImportError.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "vnvspec"

# PyPI name -> import name mapping for cases where they differ
_PYPI_TO_IMPORT: dict[str, str] = {
    "pyyaml": "yaml",
    "tomli-w": "tomli_w",
    "openpyxl": "openpyxl",
}

# Standard library top-level module names (3.11+)
_STDLIB = set(sys.stdlib_module_names)


def _parse_pyproject_deps() -> set[str]:
    """Return import names from [project.dependencies] and [project.optional-dependencies]."""
    import tomllib

    with (ROOT / "pyproject.toml").open("rb") as f:
        cfg = tomllib.load(f)
    import_names: set[str] = set()
    # Main dependencies
    for dep in cfg.get("project", {}).get("dependencies", []):
        pypi_name = re.split(r"[>=<!\[;]", dep)[0].strip().lower()
        if pypi_name == "vnvspec":
            continue
        import_names.add(_PYPI_TO_IMPORT.get(pypi_name, pypi_name.replace("-", "_")))
    # Optional dependencies
    for deps in cfg.get("project", {}).get("optional-dependencies", {}).values():
        for dep in deps:
            pypi_name = re.split(r"[>=<!\[;]", dep)[0].strip().lower()
            if pypi_name == "vnvspec":
                continue
            import_names.add(_PYPI_TO_IMPORT.get(pypi_name, pypi_name.replace("-", "_")))
    return import_names


def _type_checking_lines(tree: ast.AST) -> set[int]:
    """Return line numbers inside `if TYPE_CHECKING:` blocks."""
    lines: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        name = getattr(test, "id", None) or getattr(test, "attr", None)
        if name == "TYPE_CHECKING":
            for child in ast.walk(node):
                if hasattr(child, "lineno"):
                    lines.add(child.lineno)
    return lines


def _extract_top_level(name: str) -> str | None:
    """Return the top-level package name if it's a third-party import."""
    top = name.split(".", maxsplit=1)[0]
    if top in _STDLIB or top == "vnvspec":
        return None
    return top


def _collect_runtime_imports() -> set[str]:
    """Scan all .py files under src/vnvspec/ for third-party imports."""
    third_party: set[str] = set()
    for py_file in SRC.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        except SyntaxError:
            continue
        tc_lines = _type_checking_lines(tree)
        for node in ast.walk(tree):
            if node.lineno in tc_lines if hasattr(node, "lineno") else False:
                continue
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = _extract_top_level(alias.name)
                    if top:
                        third_party.add(top)
            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue
                if node.module and (top := _extract_top_level(node.module)):
                    third_party.add(top)
    return third_party


@pytest.mark.vnvspec("REQ-SELF-PKG-001")
def test_all_runtime_imports_declared() -> None:
    """Every third-party import in src/vnvspec/ must be in pyproject.toml dependencies."""
    declared = _parse_pyproject_deps()
    used = _collect_runtime_imports()
    undeclared = used - declared
    assert not undeclared, (
        f"Third-party packages imported but not in [project.dependencies]: {sorted(undeclared)}. "
        f"Add them to pyproject.toml."
    )
