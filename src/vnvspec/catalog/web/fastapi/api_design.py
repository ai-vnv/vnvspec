"""FastAPI API design best practices.

This catalog reflects published best practices for FastAPI as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://fastapi.tiangolo.com/
- https://datatracker.ietf.org/doc/rfc9457/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: fastapi>=0.110,<1.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "fastapi>=0.110,<1.0"


def api_design() -> list[Requirement]:
    """FastAPI API design requirements."""
    return [
        Requirement(
            id="CAT-FPI-API-001",
            statement=(
                "Error responses shall conform to RFC 9457 (Problem Details for "
                "HTTP APIs) with type, title, status, detail, and instance fields."
            ),
            rationale=(
                "Standardized error responses enable clients to handle errors "
                "programmatically without parsing free-text messages."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All 4xx and 5xx responses have content-type application/problem+json.",
                "Response bodies contain type, title, and status fields.",
            ],
            source=["https://datatracker.ietf.org/doc/rfc9457/"],
            priority="high",
        ),
        Requirement(
            id="CAT-FPI-API-002",
            statement=(
                "List endpoints shall implement cursor-based or offset pagination "
                "with explicit total, next, and prev links in the response."
            ),
            rationale=(
                "Unpaginated list endpoints return unbounded result sets that "
                "exhaust server memory and client bandwidth."
            ),
            verification_method="test",
            acceptance_criteria=[
                "List endpoints accept page/limit or cursor parameters.",
                "Responses include total count and navigation links.",
                "A maximum page size is enforced.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="high",
            standards={"owasp_api_top10_2023": ["API4:2023"]},
        ),
        Requirement(
            id="CAT-FPI-API-003",
            statement=(
                "PUT and DELETE endpoints shall be idempotent: repeated identical "
                "requests shall produce the same result as a single request."
            ),
            rationale=(
                "Idempotency prevents duplicate side effects from retries caused "
                "by network errors, client timeouts, or load balancer retries."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Two identical PUT requests produce the same state.",
                "Two identical DELETE requests return the same status.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="high",
        ),
        Requirement(
            id="CAT-FPI-API-004",
            statement=(
                "Every endpoint shall have a response_model set that defines "
                "the exact shape of successful responses."
            ),
            rationale=(
                "Explicit response models prevent accidental data leaks, enable "
                "automatic OpenAPI documentation, and serve as a contract between "
                "backend and frontend teams."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All endpoints have response_model or response_class set.",
                "OpenAPI spec includes response schemas for all endpoints.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="high",
            standards={"owasp_api_top10_2023": ["API3:2023"]},
        ),
        Requirement(
            id="CAT-FPI-API-005",
            statement=(
                "Path parameters and query parameters shall use Pydantic models "
                "or annotated types with explicit validation constraints."
            ),
            rationale=(
                "Unvalidated input parameters are the root cause of injection "
                "vulnerabilities and data corruption. FastAPI's Pydantic integration "
                "provides free input validation when used correctly."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All path and query parameters use typed annotations.",
                "Invalid parameter values return 422 with validation details.",
            ],
            source=[
                "https://fastapi.tiangolo.com/",
                "https://owasp.org/API-Security/editions/2023/en/0x00-header/",
            ],
            priority="blocking",
            standards={"owasp_api_top10_2023": ["API8:2023"]},
        ),
        Requirement(
            id="CAT-FPI-API-006",
            statement=(
                "The API shall version its endpoints using URL path versioning "
                "(e.g., /v1/) or header-based versioning, with the strategy "
                "documented in the OpenAPI spec."
            ),
            rationale=(
                "Unversioned APIs cannot evolve without breaking clients. "
                "Explicit versioning enables backward-compatible changes."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "API endpoints include a version prefix or accept a version header.",
                "The versioning strategy is documented.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="medium",
            standards={"owasp_api_top10_2023": ["API9:2023"]},
        ),
    ]
