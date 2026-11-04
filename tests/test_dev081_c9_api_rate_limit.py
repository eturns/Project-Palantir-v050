"""DEV-081-C9 — FastAPI rate-limit integration tests.

Author: Edward Turns (Project Lead)
"""

import asyncio

from starlette.requests import Request

from web.backend.rate_limit import SlidingWindowRateLimiter


def make_request(path: str, ip: str) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": [],
        "client": (ip, 12345),
        "scheme": "http",
        "server": ("testserver", 80),
    }
    return Request(scope)


def test_rate_limiter_uses_request_client_ip():
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60)

    first = make_request("/api/v1/analyse", "192.0.2.10")
    second = make_request("/api/v1/analyse", "192.0.2.20")

    assert limiter.allow(first.client.host, now=100.0)
    assert limiter.allow(second.client.host, now=100.0)
    assert not limiter.allow(first.client.host, now=100.0)


def test_rate_limiter_does_not_trust_spoofed_headers():
    request = make_request("/api/v1/analyse", "192.0.2.10")
    request.scope["headers"] = [
        (b"x-forwarded-for", b"203.0.113.99"),
    ]

    assert request.client.host == "192.0.2.10"

def test_middleware_returns_429_after_ten_requests():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from web.backend.rate_limit import AnalysisRateLimitMiddleware

    test_app = FastAPI()
    calls = []

    @test_app.post("/api/v1/analyse")
    def analyse():
        calls.append(1)
        return {"status": "ok"}

    @test_app.get("/health")
    def health():
        return {"status": "ok"}

    test_app.add_middleware(
        AnalysisRateLimitMiddleware,
        limit=10,
        window_seconds=60,
    )

    with TestClient(test_app) as client:
        for _ in range(10):
            assert client.post("/api/v1/analyse").status_code == 200

        response = client.post("/api/v1/analyse")

        assert response.status_code == 429
        assert len(calls) == 10
        assert client.get("/health").status_code == 200

def test_rejected_upload_is_not_parsed():
    from fastapi import FastAPI, File, UploadFile
    from fastapi.testclient import TestClient

    from web.backend.rate_limit import AnalysisRateLimitMiddleware

    test_app = FastAPI()
    processed_files = []

    @test_app.post("/api/v1/analyse")
    def analyse(file: UploadFile = File(...)):
        processed_files.append(file.filename)
        return {"filename": file.filename}

    test_app.add_middleware(
        AnalysisRateLimitMiddleware,
        limit=1,
        window_seconds=60,
    )

    with TestClient(test_app) as client:
        first = client.post(
            "/api/v1/analyse",
            files={"file": ("first.json", b"{}", "application/json")},
        )
        assert first.status_code == 200

        second = client.post(
            "/api/v1/analyse",
            files={"file": ("second.json", b"{}", "application/json")},
        )
        assert second.status_code == 429

    assert processed_files == ["first.json"]

def test_production_app_rate_limit():
    from fastapi.testclient import TestClient

    from web.backend.app import app

    with TestClient(app) as client:
        for _ in range(10):
            response = client.post(
                "/api/v1/analyse",
                files={
                    "file": (
                        "invalid.json",
                        b"{invalid",
                        "application/json",
                    ),
                },
            )
            assert response.status_code == 400

        response = client.post(
            "/api/v1/analyse",
            files={
                "file": (
                    "invalid.json",
                    b"{invalid",
                    "application/json",
                ),
            },
        )

        assert response.status_code == 429
        assert response.headers["retry-after"] == "60"
        assert client.get("/health").status_code == 200
