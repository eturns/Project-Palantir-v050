"""DEV-079-A3-6C — multi-army web API parity tests.

Author: Edward Turns (Project Lead)

Successful armies must match the desktop.
Known unsupported fixture must fail consistently and safely.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from desktop_analysis_adapter import run_analysis
from web.backend.app import app
from web.backend.result_mapper import build_web_analysis_result


FIXTURES = Path(__file__).resolve().parent / "fixtures"

SUPPORTED_ARMIES = (
    "dol_guldur_700.json",
    "goblin_town_700_horde.json",
    "smaug.json",
)

IRON_HILLS = "iron_hills_army.json"

client = TestClient(app)


def upload(filename):
    path = FIXTURES / filename
    assert path.is_file()

    return client.post(
        "/api/v1/analyse",
        files={
            "file": (
                filename,
                path.read_bytes(),
                "application/json",
            ),
        },
    )


@pytest.mark.parametrize("filename", SUPPORTED_ARMIES)
def test_web_api_matches_existing_engine(filename):
    path = FIXTURES / filename

    desktop = run_analysis(str(path))
    assert desktop is not None

    expected = build_web_analysis_result(desktop)

    response = upload(filename)

    assert response.status_code == 200, response.text[:500]
    assert response.json() == expected

    analysis = response.json()["analysis"]

    assert analysis["total_points"] > 0
    assert analysis["model_count"] >= 1
    assert isinstance(analysis["metrics"], list)
    assert isinstance(analysis["scenarios"], list)

    provisional = analysis["provisional_capabilities"]

    assert provisional["display_only"] is True
    assert provisional["production_scoring_changed"] is False
    assert (
        provisional[
            "defence_independent_composite_weighting_allowed"
        ]
        is False
    )
    assert len(provisional["metrics"]) == 11


@pytest.mark.parametrize("filename", SUPPORTED_ARMIES)
def test_repeated_web_analysis_is_stable(filename):
    first = upload(filename)
    second = upload(filename)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_iron_hills_existing_engine_rejects_incomplete_shooting(capsys):
    path = FIXTURES / IRON_HILLS

    desktop = run_analysis(str(path))
    output = capsys.readouterr().out

    assert desktop is None
    assert "All ranged weapons must be mechanically complete" in output


def test_iron_hills_web_api_rejects_incomplete_shooting():
    first = upload(IRON_HILLS)
    second = upload(IRON_HILLS)

    assert first.status_code == 422
    assert second.status_code == 422

    expected = {
        "detail": "The army could not be imported or analysed."
    }

    assert first.json() == expected
    assert second.json() == expected
