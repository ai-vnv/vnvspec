"""SQLAlchemy best-practices catalog.

This catalog reflects published best practices for SQLAlchemy 2.0 as of
2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://docs.sqlalchemy.org/en/20/
- https://docs.sqlalchemy.org/en/20/core/pooling.html
- https://alembic.sqlalchemy.org/en/latest/
- https://www.cosmicpython.com/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: sqlalchemy>=2.0,<3.0
Last reviewed: 2026-04-17
"""

from vnvspec.catalog.web.sqlalchemy.schema import schema
from vnvspec.catalog.web.sqlalchemy.session import session
from vnvspec.catalog.web.sqlalchemy.transactions import transactions

__compatible_with__ = "sqlalchemy>=2.0,<3.0"

__all__ = [
    "schema",
    "session",
    "transactions",
]
