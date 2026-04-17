# Test Runner Patterns

Three patterns for organizing V&V test suites, adapted from real-world integration experience.

## Pattern 1: Static Analysis Tests

Tests that validate the spec itself — no running system required.

```python
import pytest
from vnvspec import Spec

@pytest.mark.vnvspec("REQ-SPEC-001")
def test_all_requirements_have_rationale(spec: Spec):
    for req in spec.requirements:
        assert req.rationale, f"{req.id} has no rationale"

@pytest.mark.vnvspec("REQ-SPEC-002")
def test_requirement_quality(spec: Spec):
    for req in spec.requirements:
        violations = req.check_quality(profile="web-app")
        errors = [v for v in violations if v.severity == "error"]
        assert not errors, f"{req.id}: {errors}"
```

## Pattern 2: Live API Tests

Tests that hit a running service to verify functional requirements.

```python
import httpx
import pytest

@pytest.mark.vnvspec("REQ-API-001")
def test_health_endpoint(api_url: str):
    r = httpx.get(f"{api_url}/health")
    assert r.status_code == 200

@pytest.mark.vnvspec("REQ-API-002")
def test_auth_required(api_url: str):
    r = httpx.get(f"{api_url}/protected")
    assert r.status_code == 401
```

## Pattern 3: Build Verification Tests

Tests that verify build artifacts after CI produces them.

```python
import pytest
from pathlib import Path

@pytest.mark.vnvspec("REQ-BUILD-001")
def test_docker_image_exists():
    result = subprocess.run(["docker", "images", "-q", "myapp:latest"], capture_output=True)
    assert result.stdout.strip(), "Docker image not built"

@pytest.mark.vnvspec("REQ-BUILD-002")
def test_migration_scripts_present():
    migrations = list(Path("migrations").glob("*.sql"))
    assert len(migrations) > 0
```

## Combining patterns

Run each pattern in a separate pytest session or with markers:

```bash
# Static checks (no infrastructure needed)
pytest -m "static" --vnvspec-spec=spec.yaml --vnvspec-report=static.json

# Live API tests (requires running service)
pytest -m "live" --vnvspec-spec=spec.yaml --vnvspec-report=live.json

# Build verification (requires build artifacts)
pytest -m "build" --vnvspec-spec=spec.yaml --vnvspec-report=build.json
```
