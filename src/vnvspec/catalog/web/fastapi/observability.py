"""FastAPI observability best practices.

This catalog reflects published best practices for FastAPI as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://fastapi.tiangolo.com/
- https://cheatsheetseries.owasp.org/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: fastapi>=0.110,<1.0
Last reviewed: 2026-04-17
"""

from __future__ import annotations

from vnvspec.core.requirement import Requirement

__compatible_with__ = "fastapi>=0.110,<1.0"


def observability() -> list[Requirement]:
    """FastAPI observability requirements."""
    return [
        Requirement(
            id="CAT-FPI-OBS-001",
            statement=(
                "The application shall use structured logging (JSON format) "
                "via structlog or stdlib logging with a JSON formatter."
            ),
            rationale=(
                "Structured logs are machine-parseable, enabling log aggregation, "
                "alerting, and analysis. Unstructured logs require fragile regex parsing."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Log output is valid JSON with at least timestamp, level, and message fields.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="high",
            standards={"iso_25010": ["4.7.3"], "incose_se_handbook": ["5.7"]},
        ),
        Requirement(
            id="CAT-FPI-OBS-002",
            statement=(
                "Every request shall carry a correlation ID (X-Request-ID header) "
                "propagated through middleware to all log entries and downstream "
                "service calls."
            ),
            rationale=(
                "Correlation IDs enable end-to-end request tracing across services. "
                "Without them, debugging distributed systems is infeasible."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Responses include X-Request-ID header.",
                "Log entries for a request share the same correlation ID.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="high",
            standards={"iso_25010": ["4.7.3"]},
        ),
        Requirement(
            id="CAT-FPI-OBS-003",
            statement=(
                "The application shall expose /health and /ready endpoints "
                "that return the liveness and readiness status respectively."
            ),
            rationale=(
                "Health and readiness probes are required by Kubernetes and "
                "most deployment platforms. /health checks process liveness; "
                "/ready checks dependency availability."
            ),
            verification_method="test",
            acceptance_criteria=[
                "GET /health returns 200 with a JSON body.",
                "GET /ready returns 200 when all dependencies are available, 503 otherwise.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="blocking",
            standards={"iso_25010": ["4.5.2"]},
        ),
        Requirement(
            id="CAT-FPI-OBS-004",
            statement=(
                "The application shall log the HTTP method, path, status code, "
                "and response time for every request."
            ),
            rationale=(
                "Access logs are the minimum viable observability. Without them, "
                "debugging production issues and tracking SLA compliance is impossible."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Every request produces a log entry with method, path, status, "
                "and duration_ms fields.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="high",
        ),
        Requirement(
            id="CAT-FPI-OBS-005",
            statement=(
                "The application shall not log sensitive data (passwords, tokens, "
                "PII) in request or response bodies."
            ),
            rationale=(
                "Logging sensitive data creates a security incident when logs are "
                "accessed by unauthorized parties. Log redaction must be enforced "
                "at the middleware level."
            ),
            verification_method="test",
            acceptance_criteria=[
                "Request bodies containing password fields are redacted in logs.",
                "Authorization headers are not logged in full.",
            ],
            source=["https://cheatsheetseries.owasp.org/"],
            priority="blocking",
            standards={
                "owasp_api_top10_2023": ["API8:2023"],
                "iso_25010": ["4.6.1"],
            },
        ),
        Requirement(
            id="CAT-FPI-OBS-006",
            statement=(
                "The application shall emit metrics for request count, error rate, "
                "and latency percentiles (p50, p95, p99) per endpoint."
            ),
            rationale=(
                "RED metrics (Rate, Errors, Duration) are the standard for API "
                "observability. Without per-endpoint metrics, performance regressions "
                "and partial outages go undetected."
            ),
            verification_method="inspection",
            acceptance_criteria=[
                "Prometheus or OpenTelemetry metrics are configured.",
                "Metrics include request_count, error_count, and latency histograms.",
            ],
            source=["https://fastapi.tiangolo.com/"],
            priority="medium",
            standards={"incose_se_handbook": ["5.7"], "iso_25010": ["4.2.1"]},
        ),
    ]
