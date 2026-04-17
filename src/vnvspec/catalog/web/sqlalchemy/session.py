"""SQLAlchemy session management best practices.

This catalog reflects published best practices for SQLAlchemy 2.0 as of
2026-04-17. It is a baseline, not a substitute for expert review.

Sources:
- https://docs.sqlalchemy.org/en/20/
- https://docs.sqlalchemy.org/en/20/core/pooling.html

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: sqlalchemy>=2.0,<3.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "sqlalchemy>=2.0,<3.0"


def session() -> list[Requirement]:
    """SQLAlchemy session management requirements."""
    return [
        Requirement(
            id="CAT-SQA-SESS-001",
            statement=(
                "The application shall use a session-per-request pattern, creating "
                "a new session for each HTTP request via FastAPI Depends() or "
                "ASGI middleware."
            ),
            rationale=(
                "Shared sessions across requests cause data leaks between users "
                "and race conditions. Session-per-request is the standard pattern "
                "for web applications."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Each HTTP request receives a fresh session instance.",
                "The session is closed at the end of the request.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="blocking",
        ),
        Requirement(
            id="CAT-SQA-SESS-002",
            statement=(
                "The connection pool size shall be configured relative to the "
                "number of application workers, with pool_size and max_overflow "
                "set explicitly."
            ),
            rationale=(
                "Default pool sizes are often too small for production workloads. "
                "pool_size * workers should not exceed the database's max_connections."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "create_engine() specifies pool_size and max_overflow explicitly.",
                "Total pool capacity across all workers is documented.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/core/pooling.html"],
            priority="high",
        ),
        Requirement(
            id="CAT-SQA-SESS-003",
            statement=(
                "The expire_on_commit setting shall be chosen explicitly based "
                "on the application's access pattern, not left as the default."
            ),
            rationale=(
                "expire_on_commit=True (default) triggers lazy-load queries after "
                "commit, which may cause N+1 issues. expire_on_commit=False risks "
                "stale data. The choice must be intentional."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Session creation specifies expire_on_commit explicitly.",
                "The rationale for the chosen setting is documented.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="medium",
        ),
        Requirement(
            id="CAT-SQA-SESS-004",
            statement=(
                "The connection pool shall configure pool_pre_ping=True or an "
                "equivalent connection health check to detect stale connections."
            ),
            rationale=(
                "Database connections go stale from timeouts, network interruptions, "
                "or database restarts. pool_pre_ping=True tests connections before "
                "use, preventing 'connection closed' errors in production."
            ),
            verification_method="test",
            acceptance_criteria=[
                "create_engine() includes pool_pre_ping=True.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/core/pooling.html"],
            priority="high",
        ),
        Requirement(
            id="CAT-SQA-SESS-005",
            statement=(
                "The application shall configure pool_recycle to a value below "
                "the database server's wait_timeout to prevent connection resets."
            ),
            rationale=(
                "If pool_recycle exceeds the database's wait_timeout, connections "
                "are silently closed by the server, causing errors on the next use."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "pool_recycle is set and is less than the database wait_timeout.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/core/pooling.html"],
            priority="medium",
        ),
        Requirement(
            id="CAT-SQA-SESS-006",
            statement=(
                "The application shall use scoped_session or async_scoped_session "
                "only when a genuine thread-local or task-local session scope is "
                "needed, and shall document the scoping strategy."
            ),
            rationale=(
                "scoped_session is often used incorrectly as a global session, "
                "causing cross-request data leaks. It should only be used when "
                "the framework does not provide request-scoped session management."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "scoped_session usage is documented with justification.",
                "The scoping key (thread ID, task ID) is explicitly set.",
            ],
            source=["https://docs.sqlalchemy.org/en/20/"],
            priority="medium",
        ),
    ]
