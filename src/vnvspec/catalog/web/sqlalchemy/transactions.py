"""SQLAlchemy transaction management best practices.

This catalog reflects published best practices for SQLAlchemy 2.0 as of
2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://docs.sqlalchemy.org/en/20/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: sqlalchemy>=2.0,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "sqlalchemy>=2.0,<3.0"


def transactions() -> list[Requirement]:
    """SQLAlchemy transaction management requirements."""
    return [
        Requirement(
            id="CAT-SQA-TXN-001",
            statement=(
                "All database operations shall use explicit transaction contexts "
                "via session.begin() or async with engine.begin(), not implicit "
                "autocommit."
            ),
            rationale=(
                "SQLAlchemy 2.0 removes implicit autocommit. Explicit transactions "
                "prevent accidental partial commits and make rollback boundaries clear."
            ),
            verification_method="test",
            acceptance_criteria=[
                "No database operations occur outside a session.begin() context.",
                "All write paths have explicit commit or rollback.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="blocking",
            standards={"iso_25010": ["4.6.2"], "nasa_se_handbook": ["5.3"]},
        ),
        Requirement(
            id="CAT-SQA-TXN-002",
            statement=(
                "Every database error handling path shall include an explicit "
                "session.rollback() or shall use a context manager that handles "
                "rollback automatically."
            ),
            rationale=(
                "Unrolled-back transactions hold database locks, cause connection "
                "pool exhaustion, and leave the session in an unusable state."
            ),
            verification_method="test",
            acceptance_criteria=[
                "A simulated database error triggers rollback.",
                "The session is usable after the error is handled.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="blocking",
            standards={"iso_25010": ["4.5.4"]},
        ),
        Requirement(
            id="CAT-SQA-TXN-003",
            statement=(
                "The transaction isolation level shall be documented for each "
                "database operation that requires specific isolation guarantees."
            ),
            rationale=(
                "The default isolation level (READ COMMITTED for most databases) "
                "is insufficient for operations that require repeatable reads or "
                "serializable consistency."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Operations requiring non-default isolation levels are documented.",
                "Isolation level overrides use execution_options(isolation_level=...).",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="high",
        ),
        Requirement(
            id="CAT-SQA-TXN-004",
            statement=(
                "Long-running transactions shall be avoided by keeping transaction "
                "scope as narrow as possible and by not holding transactions open "
                "across user-facing I/O boundaries."
            ),
            rationale=(
                "Long transactions hold row locks and connection pool slots, "
                "increasing contention and risk of deadlocks."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "No transaction spans a user-facing HTTP request/response cycle "
                "beyond the database operation itself.",
            ],
            source=[
                "https://docs.sqlalchemy.org/en/20/",
                "https://www.cosmicpython.com/",
            ],
            priority="high",
            standards={"iso_25010": ["4.2.1"]},
        ),
        Requirement(
            id="CAT-SQA-TXN-005",
            statement=(
                "Bulk insert and update operations shall use SQLAlchemy's bulk "
                "methods or Core insert/update constructs to avoid N+1 performance "
                "issues."
            ),
            rationale=(
                "ORM-level individual inserts generate N separate SQL statements. "
                "Bulk operations reduce database round-trips by orders of magnitude."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Bulk operations use session.bulk_save_objects(), insert().values(), "
                "or equivalent bulk methods.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-SQA-TXN-006",
            statement=(
                "The application shall implement retry logic with exponential "
                "backoff for transient database errors (connection timeouts, "
                "deadlocks, serialization failures)."
            ),
            rationale=(
                "Transient database errors are normal in production. Without retry "
                "logic, temporary issues cascade into user-visible errors."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Transient errors trigger a retry with backoff.",
                "The maximum retry count is configurable.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="medium",
            standards={"iso_25010": ["4.5.3"]},
        ),
    ]
