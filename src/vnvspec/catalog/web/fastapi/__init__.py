"""FastAPI best-practices catalog.

This catalog reflects published best practices for FastAPI as of 2026-04-17.
It is a baseline, not a substitute for expert review.

Sources:
- https://fastapi.tiangolo.com/
- https://owasp.org/API-Security/editions/2023/en/0x00-header/
- https://owasp.org/www-project-application-security-verification-standard/
- https://datatracker.ietf.org/doc/rfc9457/

Maintainer: AI V&V Lab, KFUPM (mansur.arief@kfupm.edu.sa)
Compatible with: fastapi>=0.110,<1.0
Last reviewed: 2026-04-17

Note: OWASP ASVS registry not yet bundled; standards mappings reference
owasp_api_top10_2023 keys only.
"""

from vnvspec.catalog.web.fastapi.api_design import api_design
from vnvspec.catalog.web.fastapi.observability import observability
from vnvspec.catalog.web.fastapi.security import security_baseline

__compatible_with__ = "fastapi>=0.110,<1.0"

__all__ = [
    "api_design",
    "observability",
    "security_baseline",
]
