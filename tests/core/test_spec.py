"""Tests for the Spec model."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vnvspec.core.errors import SpecError
from vnvspec.core.evidence import Evidence
from vnvspec.core.hazard import Hazard
from vnvspec.core.requirement import Requirement
from vnvspec.core.spec import Spec


@pytest.fixture()
def sample_req() -> Requirement:
    return Requirement(
        id="REQ-001",
        statement="The system shall produce valid outputs.",
        rationale="Safety.",
        verification_method="test",
        acceptance_criteria=["All outputs valid."],
    )


@pytest.fixture()
def sample_hazard() -> Hazard:
    return Hazard(
        id="HAZ-001",
        description="Incorrect classification.",
        severity="S3",
        exposure="E4",
        controllability="C3",
        asil="D",
        mitigations=["REQ-001"],
    )


class TestSpecConstruction:
    def test_empty_spec(self) -> None:
        spec = Spec(name="empty")
        assert spec.name == "empty"
        assert len(spec.requirements) == 0

    def test_with_requirements(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        assert len(spec.requirements) == 1

    def test_duplicate_requirement_ids(self, sample_req: Requirement) -> None:
        with pytest.raises(SpecError, match="Duplicate requirement IDs"):
            Spec(name="bad", requirements=[sample_req, sample_req])

    def test_duplicate_hazard_ids(self, sample_hazard: Hazard) -> None:
        with pytest.raises(SpecError, match="Duplicate hazard IDs"):
            Spec(name="bad", hazards=[sample_hazard, sample_hazard])


class TestSpecLookup:
    def test_get_requirement(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        assert spec.get_requirement("REQ-001") == sample_req

    def test_get_requirement_not_found(self) -> None:
        spec = Spec(name="test")
        with pytest.raises(SpecError, match="not found"):
            spec.get_requirement("REQ-999")

    def test_get_hazard(self, sample_hazard: Hazard) -> None:
        spec = Spec(name="test", hazards=[sample_hazard])
        assert spec.get_hazard("HAZ-001") == sample_hazard

    def test_get_hazard_not_found(self) -> None:
        spec = Spec(name="test")
        with pytest.raises(SpecError, match="not found"):
            spec.get_hazard("HAZ-999")


class TestSpecEvidence:
    def test_evidence_for(self, sample_req: Requirement) -> None:
        ev = Evidence(id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass")
        spec = Spec(name="test", requirements=[sample_req], evidence=[ev])
        assert len(spec.evidence_for("REQ-001")) == 1
        assert len(spec.evidence_for("REQ-999")) == 0

    def test_coverage_summary_empty(self) -> None:
        spec = Spec(name="test")
        assert spec.coverage_summary() == {"total": 0, "covered": 0, "uncovered": 0}

    def test_coverage_summary_partial(self, sample_req: Requirement) -> None:
        req2 = Requirement(id="REQ-002", statement="Second.", verification_method="test")
        ev = Evidence(id="EV-001", requirement_id="REQ-001", kind="test", verdict="pass")
        spec = Spec(name="test", requirements=[sample_req, req2], evidence=[ev])
        summary = spec.coverage_summary()
        assert summary == {"total": 2, "covered": 1, "uncovered": 1}


class TestSpecExtend:
    def test_extend_with_list(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        new_req = Requirement(id="REQ-NEW", statement="New.", verification_method="test")
        spec2 = spec.extend([new_req])
        assert len(spec2.requirements) == 2
        assert spec2.requirements[1].id == "REQ-NEW"

    def test_extend_with_varargs(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        r1 = Requirement(id="REQ-A", statement="A.", verification_method="test")
        r2 = Requirement(id="REQ-B", statement="B.", verification_method="test")
        spec2 = spec.extend(r1, r2)
        assert len(spec2.requirements) == 3

    def test_extend_mixed(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        r1 = Requirement(id="REQ-A", statement="A.", verification_method="test")
        r2 = Requirement(id="REQ-B", statement="B.", verification_method="test")
        r3 = Requirement(id="REQ-C", statement="C.", verification_method="test")
        spec2 = spec.extend(r1, [r2, r3])
        assert len(spec2.requirements) == 4

    def test_extend_preserves_original(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        new_req = Requirement(id="REQ-NEW", statement="New.", verification_method="test")
        spec.extend([new_req])
        assert len(spec.requirements) == 1  # original unchanged

    def test_extend_duplicate_ids_raises(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        dupe = Requirement(id="REQ-001", statement="Dupe.", verification_method="test")
        with pytest.raises(SpecError, match="Duplicate requirement IDs"):
            spec.extend([dupe])

    def test_extend_with_catalog(self) -> None:
        from vnvspec.catalog.demo import hello_world

        spec = Spec(name="demo")
        spec2 = spec.extend(hello_world())
        assert len(spec2.requirements) == 1
        assert spec2.requirements[0].id == "CAT-DEMO-001"

    def test_extend_empty(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        spec2 = spec.extend([])
        assert len(spec2.requirements) == 1


class TestSpecSerialization:
    def test_json_round_trip(self, sample_req: Requirement) -> None:
        spec = Spec(name="test", requirements=[sample_req])
        data = json.loads(spec.model_dump_json())
        spec2 = Spec.model_validate(data)
        assert spec.name == spec2.name
        assert len(spec2.requirements) == 1

    def test_yaml_round_trip(self, sample_req: Requirement, tmp_path: Path) -> None:
        spec = Spec(name="test-yaml", requirements=[sample_req])
        yaml_path = tmp_path / "spec.yaml"
        spec.to_yaml(yaml_path)
        spec2 = Spec.from_yaml(yaml_path)
        assert spec2.name == spec.name
        assert len(spec2.requirements) == 1
        assert spec2.requirements[0].id == sample_req.id
        assert spec2.requirements[0].statement == sample_req.statement

    def test_yaml_string_output(self, sample_req: Requirement) -> None:
        spec = Spec(name="test-yaml", requirements=[sample_req])
        text = spec.to_yaml()
        assert "test-yaml" in text
        assert "REQ-001" in text

    def test_yaml_round_trip_equality(self, sample_req: Requirement) -> None:
        spec = Spec(name="rt", requirements=[sample_req])
        text = spec.to_yaml()
        spec2 = Spec.model_validate(__import__("yaml").safe_load(text))
        assert spec.model_dump() == spec2.model_dump()

    def test_toml_round_trip(self, sample_req: Requirement, tmp_path: Path) -> None:
        spec = Spec(name="test-toml", requirements=[sample_req])
        toml_path = tmp_path / "spec.toml"
        spec.to_toml(toml_path)
        spec2 = Spec.from_toml(toml_path)
        assert spec2.name == spec.name
        assert len(spec2.requirements) == 1
        assert spec2.requirements[0].id == sample_req.id

    def test_toml_string_output(self, sample_req: Requirement) -> None:
        spec = Spec(name="test-toml", requirements=[sample_req])
        text = spec.to_toml()
        assert "test-toml" in text

    def test_toml_round_trip_equality(self, sample_req: Requirement) -> None:
        spec = Spec(name="rt", requirements=[sample_req])
        text = spec.to_toml()
        import tomllib

        data = tomllib.loads(text)
        spec2 = Spec.model_validate(data)
        assert spec.model_dump() == spec2.model_dump()

    def test_json_file_round_trip(self, sample_req: Requirement, tmp_path: Path) -> None:
        spec = Spec(name="test-json", requirements=[sample_req])
        json_path = tmp_path / "spec.json"
        spec.to_json(json_path)
        spec2 = Spec.from_json(json_path)
        assert spec2.name == spec.name
        assert len(spec2.requirements) == 1

    def test_yaml_invalid_raises(self, tmp_path: Path) -> None:
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text("- just a list\n- not a mapping\n")
        with pytest.raises(SpecError, match="Expected a YAML mapping"):
            Spec.from_yaml(bad_yaml)

    def test_yaml_complex_spec(self, tmp_path: Path) -> None:
        """Round-trip a spec with multiple requirements, hazards, and evidence."""
        reqs = [
            Requirement(
                id=f"REQ-{i:03d}",
                statement=f"The system shall do thing {i}.",
                rationale=f"Because {i}.",
                verification_method="test",
                acceptance_criteria=[f"Criterion {i}"],
                standards={"iso_pas_8800": [f"6.{i}.1"]},
            )
            for i in range(1, 6)
        ]
        hazards = [
            Hazard(
                id="HAZ-001",
                description="Bad thing.",
                severity="S3",
                exposure="E4",
                controllability="C3",
                asil="D",
                mitigations=["REQ-001"],
            )
        ]
        spec = Spec(
            name="complex",
            version="2.0",
            description="A complex spec.",
            requirements=reqs,
            hazards=hazards,
            metadata={"author": "test"},
        )
        yaml_path = tmp_path / "complex.yaml"
        spec.to_yaml(yaml_path)
        spec2 = Spec.from_yaml(yaml_path)
        assert spec.model_dump() == spec2.model_dump()
