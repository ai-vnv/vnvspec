"""FastAPI security best practices — OWASP API Security Top 10 2023.

This catalog reflects published best practices for FastAPI as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://owasp.org/API-Security/editions/2023/en/0x00-header/
- https://fastapi.tiangolo.com/
- https://cheatsheetseries.owasp.org/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: fastapi>=0.110,<1.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "fastapi>=0.110,<1.0"


def security_baseline() -> list[Requirement]:
    """FastAPI security requirements mapped to OWASP API Security Top 10 2023."""
    return [
        # --- API1:2023 Broken Object Level Authorization (BOLA) ---
        Requirement(
            id="CAT-FPI-SEC-001",
            statement=(
                "Every endpoint that accesses a user-owned resource shall include "
                "an authorization dependency that verifies the authenticated user "
                "owns or has access to the requested object."
            ),
            rationale=(
                "BOLA is the #1 API vulnerability. Without per-object authorization, "
                "any authenticated user can access any other user's resources by "
                "changing the object ID in the request."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Accessing another user's resource returns 403 or 404.",
                "The authorization check is implemented as a FastAPI Depends().",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="blocking",
            standards={
                "owasp_api_top10_2023": ["API1:2023"],
                "iso_sae_21434": ["10"],
                "iso_25010": ["4.6.4"],
            },
        ),
        # --- API2:2023 Broken Authentication ---
        Requirement(
            id="CAT-FPI-SEC-002",
            statement=(
                "JWT tokens shall have an expiration time (exp claim) validated "
                "on every request, and password change endpoints shall require "
                "the current password."
            ),
            rationale=(
                "Broken authentication allows attackers to impersonate users. "
                "Expired tokens and password-change without verification are "
                "the two most common authentication failures."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Expired JWT tokens are rejected with 401.",
                "Password change without current password returns 400 or 403.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="blocking",
            standards={
                "owasp_api_top10_2023": ["API2:2023"],
                "iso_25010": ["4.6.5"],
            },
        ),
        # --- API3:2023 Broken Object Property Level Authorization (BOPLA) ---
        Requirement(
            id="CAT-FPI-SEC-003",
            statement=(
                "Every endpoint returning user objects shall use a response_model "
                "that explicitly lists allowed fields, preventing internal or "
                "sensitive fields from leaking."
            ),
            rationale=(
                "BOPLA (merges 2019 Excessive Data Exposure + Mass Assignment). "
                "Without explicit response models, internal fields (password hashes, "
                "internal IDs) leak to clients."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All public endpoints have response_model set.",
                "Response bodies do not contain fields not in the response_model.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="blocking",
            standards={
                "owasp_api_top10_2023": ["API3:2023"],
                "iso_25010": ["4.6.1"],
            },
        ),
        # --- API4:2023 Unrestricted Resource Consumption ---
        Requirement(
            id="CAT-FPI-SEC-004",
            statement=(
                "The API shall enforce rate limiting, request body size limits, "
                "and query pagination to prevent unrestricted resource consumption."
            ),
            rationale=(
                "Without rate limiting and size limits, a single client can exhaust "
                "server resources. Pagination prevents unbounded query results."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Rate-limiting middleware is configured.",
                "Request body size limit is set.",
                "List endpoints enforce pagination with max page size.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="high",
            standards={"owasp_api_top10_2023": ["API4:2023"]},
        ),
        # --- API5:2023 Broken Function Level Authorization (BFLA) ---
        Requirement(
            id="CAT-FPI-SEC-005",
            statement=(
                "Admin endpoints shall use a dedicated dependency that checks "
                "for elevated roles, separate from the regular authentication "
                "dependency."
            ),
            rationale=(
                "BFLA allows regular users to access admin functions. Separate "
                "admin dependencies make the authorization boundary explicit."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Regular-user tokens are rejected on admin endpoints with 403.",
                "Admin dependencies are distinct from user-auth dependencies.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="blocking",
            standards={"owasp_api_top10_2023": ["API5:2023"]},
        ),
        # --- API6:2023 Unrestricted Access to Sensitive Business Flows ---
        Requirement(
            id="CAT-FPI-SEC-006",
            statement=(
                "Sensitive business flows (purchase, invitation, password reset) "
                "shall have abuse-detection hooks such as rate limiting, CAPTCHA, "
                "or anomaly detection."
            ),
            rationale=(
                "Sensitive business flows are targets for automated abuse (scalping, "
                "credential stuffing, invitation spam). Technical rate limiting alone "
                "is insufficient; business-level controls are needed."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Sensitive business endpoints are identified and documented.",
                "Each has at least one abuse-detection mechanism configured.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="high",
            standards={"owasp_api_top10_2023": ["API6:2023"]},
        ),
        # --- API7:2023 Server-Side Request Forgery (SSRF) ---
        Requirement(
            id="CAT-FPI-SEC-007",
            statement=(
                "Any endpoint that fetches remote URLs based on user input shall "
                "validate the URL against an allowlist of permitted domains."
            ),
            rationale=(
                "SSRF allows attackers to make the server request internal resources. "
                "URL allowlisting prevents requests to internal networks, cloud "
                "metadata endpoints, and other sensitive targets."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Requests to non-allowlisted domains are rejected.",
                "Requests to internal IP ranges (10.x, 169.254.x, 127.x) are blocked.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="blocking",
            standards={
                "owasp_api_top10_2023": ["API7:2023"],
                "iso_sae_21434": ["10"],
            },
        ),
        # --- API8:2023 Security Misconfiguration ---
        Requirement(
            id="CAT-FPI-SEC-008",
            statement=(
                "CORS shall be configured with a restrictive origin allowlist, "
                "debug mode shall be disabled in production, and error handlers "
                "shall return RFC 9457 problem+json responses without stack traces."
            ),
            rationale=(
                "Security misconfiguration (absorbs Injection from 2019). Permissive "
                "CORS, debug mode, and stack traces in errors are the most common "
                "FastAPI security misconfigurations."
            ),
            verification_method="test",
            acceptance_criteria=[
                "CORS origins do not include '*' in production.",
                "FastAPI debug=False in production.",
                "Error responses conform to RFC 9457 structure.",
            ],
            source=[
                "https://owasp.org/API-Security/editions/2023/en/0x00-header/",
                "https://datatracker.ietf.org/doc/rfc9457/",
            ],
            priority="blocking",
            standards={
                "owasp_api_top10_2023": ["API8:2023"],
                "nasa_se_handbook": ["6.5"],
                "iso_25010": ["4.6.6"],
            },
        ),
        # --- API9:2023 Improper Inventory Management ---
        Requirement(
            id="CAT-FPI-SEC-009",
            statement=(
                "The deployed API routes shall match the OpenAPI specification "
                "exactly, and deprecated endpoints shall be marked with "
                "deprecated=True in their route decorator."
            ),
            rationale=(
                "Improper inventory management means undocumented endpoints exist "
                "in production. OpenAPI spec drift creates shadow APIs that bypass "
                "security controls."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All registered routes appear in the OpenAPI spec.",
                "No undocumented routes exist in the application.",
                "Deprecated endpoints have deprecated=True set.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="high",
            standards={"owasp_api_top10_2023": ["API9:2023"]},
        ),
        # --- API10:2023 Unsafe Consumption of APIs ---
        Requirement(
            id="CAT-FPI-SEC-010",
            statement=(
                "Outbound HTTP calls to third-party APIs shall use explicit "
                "timeouts and shall validate response schemas before trusting "
                "the data."
            ),
            rationale=(
                "Unsafe consumption of APIs means blindly trusting third-party "
                "responses. Missing timeouts cause cascading failures; unvalidated "
                "responses enable injection through upstream APIs."
            ),
            verification_method="test",
            acceptance_criteria=[
                "All outbound HTTP calls have timeout configured.",
                "Third-party response bodies are validated before use.",
            ],
            source=["https://owasp.org/API-Security/editions/2023/en/0x00-header/"],
            priority="high",
            standards={
                "owasp_api_top10_2023": ["API10:2023"],
                "iso_25010": ["4.5.3"],
            },
        ),
    ]
