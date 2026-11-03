"""DEV-079-A3-4 — HTTP army analysis acceptance tests.

Author: Edward Turns (Project Lead)
"""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from web.backend.app import app


client = TestClient(app)

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "dol_guldur_700.json"
)


def upload(filename, contents):
    return client.post(
        "/api/v1/analyse",
        files={
            "file": (
                filename,
                contents,
                "application/json",
            ),
        },
    )


def test_real_dol_guldur_analysis():
    response = upload("dol_guldur.json", FIXTURE.read_bytes())

    assert response.status_code == 200, response.text

    result = response.json()

    assert result["schema_version"] == "palantir-web-analysis-v1"

    analysis = result["analysis"]

    assert analysis["army_name"] == "Eddie's choice"
    assert analysis["total_points"] == 700
    assert analysis["model_count"] == 11
    assert len(analysis["metrics"]) == 10
    assert len(analysis["scenarios"]) == 24
    assert len(
        analysis["provisional_capabilities"]["metrics"]
    ) == 11

    assert (
        analysis["provisional_capabilities"]["display_only"]
        is True
    )


def test_invalid_json_rejected():
    response = upload("invalid.json", b"{invalid JSON")

    assert response.status_code == 400


def test_wrong_structure_rejected():
    response = upload("wrong.json", b'{"hello": "world"}')

    assert response.status_code == 400


def test_oversized_upload_rejected():
    response = upload("large.json", b"x" * (1024 * 1024 + 1))

    assert response.status_code == 413


def test_non_json_extension_rejected():
    response = upload("army.txt", b'{"warbands": []}')

    assert response.status_code == 400


def test_empty_file_rejected():
    response = upload("empty.json", b"")

    assert response.status_code == 400
