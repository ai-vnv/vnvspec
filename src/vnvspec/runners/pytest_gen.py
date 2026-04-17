"""Generate pytest test files from a Spec object."""

from __future__ import annotations

import re
import textwrap

from vnvspec.core.spec import Spec


def _sanitize_id(req_id: str) -> str:
    """Turn a requirement ID into a valid Python identifier suffix."""
    return re.sub(r"[^a-zA-Z0-9]", "_", req_id).strip("_").lower()


def generate_pytest(spec: Spec) -> str:
    """Generate a pytest test file from *spec*.

    For each requirement whose ``verification_method`` is ``"test"``, a
    parametrised test function is emitted.  The function's docstring includes
    the requirement ID and statement for traceability.

    Parameters
    ----------
    spec:
        The specification to generate tests from.

    Returns
    -------
    str
        Valid Python source code suitable for writing to a ``.py`` file.
    """
    spec_name = spec.name
    lines: list[str] = [
        f'"""Auto-generated pytest tests for spec: {spec_name}."""',
        "",
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
    ]

    test_reqs = [r for r in spec.requirements if r.verification_method == "test"]

    if not test_reqs:
        lines.append("")
        return "\n".join(lines)

    for req in test_reqs:
        func_name = f"test_{_sanitize_id(req.id)}"
        criteria = req.acceptance_criteria if req.acceptance_criteria else ["True"]
        param_values = ", ".join(repr(c) for c in criteria)

        block = textwrap.dedent(f"""\
            @pytest.mark.parametrize("criterion", [{param_values}])
            def {func_name}(criterion: str) -> None:
                \"\"\"{req.id}: {req.statement}\"\"\"
                # TODO: implement verification logic for {req.id}
                assert criterion is not None
        """)
        lines.append(block)
        lines.append("")

    return "\n".join(lines)
