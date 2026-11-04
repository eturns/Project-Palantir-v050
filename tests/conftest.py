"""DEV-081-C9 — API test isolation.

Author: Edward Turns (Project Lead)
"""

import sys

import pytest


@pytest.fixture(autouse=True)
def isolate_api_rate_limit():
    """Reset API rate-limit counters around each automated test."""

    module = sys.modules.get("web.backend.app")

    if module is not None:
        module.analysis_rate_limiter.reset()

    yield

    module = sys.modules.get("web.backend.app")

    if module is not None:
        module.analysis_rate_limiter.reset()
