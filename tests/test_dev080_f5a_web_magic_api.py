"""
Project Palantír
DEV-080-F5A: Provisional Magic Web API Acceptance.

Author: Edward Turns (Project Lead)

Verifies that Magic evidence passes through
the actual FastAPI upload endpoint without
replacing existing capability or scenario scores.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from web.backend.app import app


FIXTURES = Path(__file__).resolve().parent / "fixtures"
client = TestClient(app)


@pytest.fixture(scope="module")
def api_results():
    results = {}

    for name, filename in (
        ("necromancer", "dol_guldur_700.json"),
        ("smaug", "smaug.json"),
        ("non_magic", "azogs-hunters.json"),
    ):
        path = FIXTURES / filename

        response = client.post(
            "/api/v1/analyse",
            files={
                "file": (
                    filename,
                    path.read_bytes(),
                    "application/json",
                ),
            },
        )

        assert response.status_code == 200, (
            response.text[:500]
        )

        results[name] = response.json()

    return results


def test_api_preserves_existing_schema(api_results):
    for result in api_results.values():
        assert result["schema_version"] == (
            "palantir-web-analysis-v1"
        )

        analysis = result["analysis"]

        assert len(
            analysis["provisional_capabilities"]["metrics"]
        ) == 11

        assert isinstance(analysis["scenarios"], list)
        assert len(analysis["scenarios"]) == 24


def test_necromancer_magic_api(api_results):
    magic = api_results["necromancer"][
        "analysis"
    ]["provisional_magic"]

    assert magic["lower_score"] == pytest.approx(5 / 9)
    assert magic["upper_score"] == pytest.approx(8 / 9)
    assert magic["caster_count"] == 1
    assert magic["modelled_attempts"] == 12


def test_smaug_magic_api(api_results):
    magic = api_results["smaug"][
        "analysis"
    ]["provisional_magic"]

    assert magic["lower_score"] == pytest.approx(1 / 6)
    assert magic["upper_score"] == pytest.approx(1 / 3)

    assert magic["temporary_will_spent"] == 6
    assert magic["permanent_will_remaining"] == 6
    assert "FOIL_MAGIC" in (
        magic["unverified_effect_spell_ids"]
    )


def test_non_magic_army_api(api_results):
    magic = api_results["non_magic"][
        "analysis"
    ]["provisional_magic"]

    assert magic["caster_count"] == 0
    assert magic["lower_score"] == 0
    assert magic["upper_score"] == 0

def test_existing_magic_rating_remains_unqualified(
    api_results,
):
    for result in api_results.values():
        analysis = result["analysis"]
        magic = analysis["provisional_magic"]

        assert magic["overall_magic_score"] is None
        assert magic["display_only"] is True

        existing_magic = next(
            item
            for item in analysis[
                "provisional_capabilities"
            ]["metrics"]
            if item["metric_id"] == "magic"
        )

        assert existing_magic["rating"] is None