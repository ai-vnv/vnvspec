"""SQLAlchemy schema management best practices.

This catalog reflects published best practices for SQLAlchemy 2.0 as of
2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://docs.sqlalchemy.org/en/20/
- https://alembic.sqlalchemy.org/en/latest/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: sqlalchemy>=2.0,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "sqlalchemy>=2.0,<3.0"


def schema() -> list[Requirement]:
    """SQLAlchemy schema management requirements."""
    return [
        Requirement(
            id="CAT-SQA-SCHM-001",
            statement=(
                "All schema changes shall be managed through Alembic migrations, "
                "not through manual SQL or metadata.create_all()."
            ),
            rationale=(
                "Alembic provides versioned, reversible, and auditable schema "
                "changes. Manual DDL is untracked and irreversible in production."
            ),
            verification_method="test",
            acceptance_criteria=[
                "An Alembic migrations directory exists.",
                "The current database schema matches the head migration.",
            ],
            source=["https://alembic.sqlalchemy.org/en/latest/"],
            priority="blocking",
        ),
        Requirement(
            id="CAT-SQA-SCHM-002",
            statement=(
                "Every declarative model shall set __tablename__ explicitly "
                "rather than relying on automatic table name generation."
            ),
            rationale=(
                "Automatic table names depend on class name case-folding rules "
                "that vary by database backend. Explicit names prevent surprises "
                "when switching databases or using mixins."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Every ORM model class has __tablename__ defined.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="high",
        ),
        Requirement(
            id="CAT-SQA-SCHM-003",
            statement=(
                "Every foreign key column shall have a corresponding database "
                "index to prevent full table scans on JOIN operations."
            ),
            rationale=(
                "Unindexed foreign keys cause O(n) scans on every JOIN. This is "
                "the most common SQLAlchemy performance anti-pattern."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Every ForeignKey column has index=True or is part of a composite index.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="high",
        ),
        Requirement(
            id="CAT-SQA-SCHM-004",
            statement=(
                "Columns shall use nullable=False by default and shall only be "
                "nullable when NULL has an explicit semantic meaning."
            ),
            rationale=(
                "Nullable columns introduce three-valued logic (True/False/NULL) "
                "that causes subtle query bugs. Defaulting to NOT NULL forces "
                "explicit handling of missing data."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Nullable columns have documented rationale for allowing NULL.",
                "New columns default to nullable=False.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-SQA-SCHM-005",
            statement=(
                "Every Alembic migration shall include both upgrade() and "
                "downgrade() functions to support rollback."
            ),
            rationale=(
                "Migrations without downgrade functions are irreversible. "
                "Rollback capability is essential for safe production deployments."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Every migration file has both upgrade() and downgrade() defined.",
                "Running upgrade then downgrade returns to the previous state.",
            ],
            source=["https://alembic.sqlalchemy.org/en/latest/"],
            priority="high",
        ),
        Requirement(
            id="CAT-SQA-SCHM-006",
            statement=(
                "The application shall use server-side defaults (server_default) "
                "for timestamps and auto-generated values rather than Python-side "
                "defaults."
            ),
            rationale=(
                "Python-side defaults are not visible to raw SQL queries or other "
                "applications sharing the database. Server defaults ensure "
                "consistency regardless of the access method."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Timestamp columns use server_default=func.now() or equivalent.",
                "Auto-increment columns use database-side generation.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="medium",
        ),
    ]
