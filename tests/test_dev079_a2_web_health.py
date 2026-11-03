"""DEV-079-A2 — FastAPI health and schema acceptance tests.

Author: Edward Turns (Project Lead)
"""

from fastapi.testclient import TestClient

from web.backend.app import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "application": "Project Palantír",
        "api_version": "0.1.0",
    }


def test_openapi_schema():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Project Palantír API"


def test_unknown_endpoint_returns_404():
    response = client.get("/does-not-exist")

    assert response.status_code == 404
