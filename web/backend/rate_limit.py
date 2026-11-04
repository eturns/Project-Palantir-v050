"""DEV-081-C9 — Public BETA request rate limiter.

Author: Edward Turns (Project Lead)
"""

from collections import deque
from threading import Lock
import time

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class SlidingWindowRateLimiter:
    """Thread-safe, per-client request limiter with expiry cleanup."""

    def __init__(self, limit: int = 10, window_seconds: float = 60):
        if limit < 1 or window_seconds <= 0:
            raise ValueError("Limit and window must be positive.")

        self.limit = limit
        self.window_seconds = window_seconds
        self._requests = {}
        self._lock = Lock()

    def allow(self, client_id: str, *, now: float) -> bool:
        """Return True if the client may make another request."""


        with self._lock:
            cutoff = now - self.window_seconds

            # Remove expired timestamps and inactive visitors.
            for visitor in list(self._requests):
                timestamps = self._requests[visitor]

                while timestamps and timestamps[0] <= cutoff:
                    timestamps.popleft()

                if not timestamps:
                    del self._requests[visitor]

            timestamps = self._requests.setdefault(client_id, deque())

            if len(timestamps) >= self.limit:
                return False

            timestamps.append(now)
            return True

    def reset(self) -> None:
        """Clear request history; intended for test isolation."""
        with self._lock:
            self._requests.clear()

class AnalysisRateLimitMiddleware:
    """Limit analysis requests before FastAPI parses uploaded files."""

    def __init__(
        self,
        app: ASGIApp,
        limit: int = 10,
        window_seconds: float = 60,
        limiter: SlidingWindowRateLimiter | None = None,
    ):
        self.app = app
        self.limiter = (
            limiter
            if limiter is not None
            else SlidingWindowRateLimiter(
                limit=limit,
                window_seconds=window_seconds,
            )
        )


    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if (
            scope["type"] != "http"
            or scope.get("path") != "/api/v1/analyse"
            or scope.get("method") != "POST"
        ):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_ip = client[0] if client else "unknown"

        if not self.limiter.allow(
            client_ip,
            now=time.monotonic(),
        ):
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many army analyses. Please try again shortly."
                },
                headers={"Retry-After": "60"},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)