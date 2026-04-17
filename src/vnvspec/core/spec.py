"""Spec model — a complete V&V specification.

A :class:`Spec` aggregates requirements, contracts, ODDs, hazards, and
evidence into a single, coherent specification document.

Example:
    >>> from vnvspec.core.requirement import Requirement
    >>> req = Requirement(
    ...     id="REQ-001",
    ...     statement="The system shall produce valid outputs.",
    ...     rationale="Safety requirement.",
    ...     verification_method="test",
    ...     acceptance_criteria=["All outputs are valid."],
    ... )
    >>> spec = Spec(name="my-system", requirements=[req])
    >>> spec.name
    'my-system'
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Self

import tomli_w
import yaml
from pydantic import BaseModel, Field, model_validator

from vnvspec.core.contract import IOContract
from vnvspec.core.errors import SpecError
from vnvspec.core.evidence import Evidence
from vnvspec.core.hazard import Hazard
from vnvspec.core.odd import ODD
from vnvspec.core.requirement import Requirement


class Spec(BaseModel):
    """A complete V&V specification.

    Example:
        >>> spec = Spec(name="empty-spec")
        >>> len(spec.requirements)
        0
    """

    model_config = {"frozen": True}

    _YAML_DUMP_KWARGS: dict[str, Any] = {
        "default_flow_style": False,
        "sort_keys": False,
        "allow_unicode": True,
    }

    name: str = Field(description="Specification name.")
    version: str = Field(default="0.1.0", description="Specification version.")
    description: str = Field(default="", description="Human-readable description.")
    requirements: list[Requirement] = Field(
        default_factory=list, description="List of requirements."
    )
    contracts: list[IOContract] = Field(default_factory=list, description="List of IO contracts.")
    odds: list[ODD] = Field(default_factory=list, description="List of operational design domains.")
    hazards: list[Hazard] = Field(default_factory=list, description="List of identified hazards.")
    evidence: list[Evidence] = Field(default_factory=list, description="Collected evidence.")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary additional metadata."
    )

    @model_validator(mode="after")
    def _validate_unique_ids(self) -> Spec:
        """Ensure all requirement and hazard IDs are unique."""
        req_ids = [r.id for r in self.requirements]
        if len(req_ids) != len(set(req_ids)):
            seen: set[str] = set()
            dupes: list[str] = []
            for rid in req_ids:
                if rid in seen:
                    dupes.append(rid)
                seen.add(rid)
            raise SpecError(f"Duplicate requirement IDs: {dupes}")

        haz_ids = [h.id for h in self.hazards]
        if len(haz_ids) != len(set(haz_ids)):
            seen = set()
            dupes = []
            for hid in haz_ids:
                if hid in seen:
                    dupes.append(hid)
                seen.add(hid)
            raise SpecError(f"Duplicate hazard IDs: {dupes}")
        return self

    def get_requirement(self, requirement_id: str) -> Requirement:
        """Look up a requirement by ID.

        Raises :class:`SpecError` if not found.

        Example:
            >>> from vnvspec.core.requirement import Requirement
            >>> req = Requirement(id="REQ-001", statement="Test.", verification_method="test")
            >>> spec = Spec(name="s", requirements=[req])
            >>> spec.get_requirement("REQ-001").id
            'REQ-001'
        """
        for req in self.requirements:
            if req.id == requirement_id:
                return req
        raise SpecError(
            f"Requirement '{requirement_id}' not found. "
            f"Available: {[r.id for r in self.requirements]}"
        )

    def get_hazard(self, hazard_id: str) -> Hazard:
        """Look up a hazard by ID.

        Raises :class:`SpecError` if not found.

        Example:
            >>> from vnvspec.core.hazard import Hazard
            >>> h = Hazard(
            ...     id="HAZ-001", description="Test.",
            ...     severity="S1", exposure="E1", controllability="C1", asil="QM",
            ... )
            >>> spec = Spec(name="s", hazards=[h])
            >>> spec.get_hazard("HAZ-001").id
            'HAZ-001'
        """
        for haz in self.hazards:
            if haz.id == hazard_id:
                return haz
        raise SpecError(
            f"Hazard '{hazard_id}' not found. Available: {[h.id for h in self.hazards]}"
        )

    def evidence_for(self, requirement_id: str) -> list[Evidence]:
        """Return all evidence linked to a requirement.

        Example:
            >>> spec = Spec(name="s")
            >>> spec.evidence_for("REQ-001")
            []
        """
        return [e for e in self.evidence if e.requirement_id == requirement_id]

    def extend(self, *additional: Requirement | Iterable[Requirement]) -> Self:
        """Return a new Spec with additional requirements appended.

        Frozen-model-safe: returns a new instance, never mutates self.
        Accepts both individual Requirements and iterables (so a catalog
        function's ``list[Requirement]`` return value can be spread or
        passed directly).

        Example:
            >>> from vnvspec.catalog.demo import hello_world
            >>> spec = Spec(name="demo")
            >>> spec2 = spec.extend(hello_world())
            >>> len(spec2.requirements)
            1
            >>> len(spec.requirements)  # original unchanged
            0
        """
        collected: list[Requirement] = []
        for item in additional:
            if isinstance(item, Requirement):
                collected.append(item)
            else:
                collected.extend(item)
        data = self.model_dump()
        data["requirements"] = [*self.requirements, *collected]
        return type(self).model_validate(data)

    def coverage_summary(self) -> dict[str, int]:
        """Return a summary of evidence coverage.

        Returns a dict with counts of requirements that are covered (have
        at least one evidence item) and uncovered.

        Example:
            >>> spec = Spec(name="s")
            >>> spec.coverage_summary()
            {'total': 0, 'covered': 0, 'uncovered': 0}
        """
        covered_ids = {e.requirement_id for e in self.evidence}
        total = len(self.requirements)
        covered = sum(1 for r in self.requirements if r.id in covered_ids)
        return {"total": total, "covered": covered, "uncovered": total - covered}

    # --- Serialization: YAML / TOML / JSON ---

    @classmethod
    def from_file(cls, path: Path | str) -> Self:
        """Load a Spec from a YAML, JSON, or TOML file (auto-detected by extension).

        Example:
            >>> import tempfile, os
            >>> from vnvspec.core.spec import Spec
            >>> s = Spec(name="t")
            >>> p = os.path.join(tempfile.mkdtemp(), "s.yaml")
            >>> _ = s.to_yaml(p)
            >>> Spec.from_file(p).name
            't'
        """
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix in (".yaml", ".yml"):
            return cls.from_yaml(path)
        if suffix == ".toml":
            return cls.from_toml(path)
        if suffix == ".json":
            return cls.from_json(path)
        raise SpecError(
            f"Unsupported file extension '{suffix}' for {path}. "
            "Use .yaml, .yml, .json, or .toml."
        )

    @classmethod
    def from_yaml(cls, path: Path | str) -> Self:
        """Load a Spec from a YAML file.

        Example:
            >>> import tempfile, os
            >>> from vnvspec.core.spec import Spec
            >>> s = Spec(name="t")
            >>> p = os.path.join(tempfile.mkdtemp(), "s.yaml")
            >>> _ = s.to_yaml(p)
            >>> Spec.from_yaml(p).name
            't'
        """
        path = Path(path)
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise SpecError(f"Expected a YAML mapping at top level in {path}")
        return cls.model_validate(data)

    @classmethod
    def from_toml(cls, path: Path | str) -> Self:
        """Load a Spec from a TOML file.

        Example:
            >>> import tempfile, os
            >>> from vnvspec.core.spec import Spec
            >>> s = Spec(name="t")
            >>> p = os.path.join(tempfile.mkdtemp(), "s.toml")
            >>> _ = s.to_toml(p)
            >>> Spec.from_toml(p).name
            't'
        """
        path = Path(path)
        with path.open("rb") as f:
            data = tomllib.load(f)
        return cls.model_validate(data)

    @classmethod
    def from_json(cls, path: Path | str) -> Self:
        """Load a Spec from a JSON file."""
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def to_yaml(self, path: Path | str | None = None) -> str:
        """Serialize to YAML. If *path* is given, also write to file.

        Returns the YAML string regardless.
        """
        data = json.loads(self.model_dump_json())
        text: str = yaml.dump(data, **self._YAML_DUMP_KWARGS)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text

    def to_toml(self, path: Path | str | None = None) -> str:
        """Serialize to TOML. If *path* is given, also write to file.

        Returns the TOML string regardless.
        """
        data = json.loads(self.model_dump_json())
        text = tomli_w.dumps(data)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text

    def to_json(self, path: Path | str | None = None) -> str:
        """Serialize to JSON. If *path* is given, also write to file.

        Returns the JSON string regardless.
        """
        text = self.model_dump_json(indent=2)
        if path is not None:
            Path(path).write_text(text, encoding="utf-8")
        return text
