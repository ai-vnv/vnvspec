"""vnvspec.catalog — pre-written Requirement objects for common packages.

.. admonition:: Preview (v0.2)

    The catalog system is in **preview** in v0.2. Only a demo module ships.
    Real catalogs (FastAPI, SQLAlchemy, PyTorch training, HuggingFace
    inference, Pyomo) ship in v0.3.

Namespace structure (planned)::

    vnvspec.catalog.web.*            # Web frameworks (FastAPI, Django, etc.)
    vnvspec.catalog.ml.*             # Machine learning (PyTorch, HuggingFace, etc.)
    vnvspec.catalog.optimization.*   # Optimization (Pyomo, Gurobi, etc.)
    vnvspec.catalog.demo             # Demo/smoke-test catalog (ships in v0.2)

API convention::

    from vnvspec.catalog.<domain>.<package> import <baseline>

Each catalog function returns ``list[Requirement]``. Compose with
:meth:`~vnvspec.core.spec.Spec.extend`::

    from vnvspec.catalog.demo import hello_world
    spec = Spec(name="my-app", requirements=[my_req])
    spec = spec.extend(hello_world())

See: https://ai-vnv.kfupm.io/vnvspec/concepts/catalog/
"""
