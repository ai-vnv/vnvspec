# Catalog (Preview)

vnvspec ships pre-written `Requirement` objects for common packages so you don't have to author every spec from scratch.

!!! warning "Preview in v0.2"
    The catalog system is in **preview** in v0.2. Only a demo module ships.
    Real catalogs (FastAPI, SQLAlchemy, PyTorch training, HuggingFace inference, Pyomo) ship in v0.3.

## API

Each catalog function returns `list[Requirement]`. Import from `vnvspec.catalog.<domain>.<package>`:

```python
from vnvspec.catalog.demo import hello_world

reqs = hello_world()  # -> list[Requirement]
```

Compose catalogs into your spec with `Spec.extend()`:

```python
from vnvspec import Spec
from vnvspec.catalog.demo import hello_world

spec = Spec(name="my-app", requirements=[my_req])
spec = spec.extend(hello_world())
```

`Spec.extend()` returns a new frozen `Spec` instance — the original is never mutated. Duplicate requirement IDs raise `SpecError` immediately.

## Planned Namespace

| Domain | Packages | Version |
|---|---|---|
| `vnvspec.catalog.web.*` | FastAPI, Django | v0.3 |
| `vnvspec.catalog.ml.*` | PyTorch training, HuggingFace inference | v0.3 |
| `vnvspec.catalog.optimization.*` | Pyomo, Gurobi | v0.3 |
| `vnvspec.catalog.demo` | Demo/smoke-test | **v0.2** (current) |
