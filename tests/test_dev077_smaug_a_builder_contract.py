"""DEV-077-SMAUG-A read-only, builder-evidence contract tests.

Place supplied smaug.json at tests/fixtures/smaug.json OR set
PALANTIR_SMAUG_JSON to its absolute path. These tests do not mutate datasets.
Run: py -3.14 -m pytest -q tests/test_dev077_smaug_a_builder_contract.py
"""
import json
import os
from pathlib import Path

import pytest

DEFAULT_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "smaug.json"

@pytest.fixture(scope="module")
def roster():
    source = Path(os.environ.get("PALANTIR_SMAUG_JSON", str(DEFAULT_FIXTURE)))
    if not source.is_file():
        pytest.fail(f"Smaug source fixture is missing: {source}")
    return json.loads(source.read_text(encoding="utf-8-sig"))


def test_builder_identity(roster):
    assert roster["edition"] == "v2024"
    assert roster["armyList"] == "Desolator of the North"
    assert roster["name"] == "Smaug"
    assert roster["version"] == "1.42.19"


def test_compulsory_single_hero_list(roster):
    assert roster["metadata"]["leaderCompulsory"] is True
    assert roster["metadata"]["maxPoints"] == 700
    assert len(roster["warbands"]) == 1
    warband = roster["warbands"][0]
    assert roster["metadata"]["leader"] == warband["id"]
    assert warband["hero"]["compulsory"] is True
    assert warband["hero"]["model_id"] == "[desolator-of-the-north] smaug"
    assert warband["hero"]["options"] == []
    assert warband["units"] == []


def test_original_builder_resources_and_totals(roster):
    wb = roster["warbands"][0]
    assert wb["hero"]["MWFW"] == [["", "3:6:0:20"]]
    assert wb["meta"]["points"] == 700
    assert wb["meta"]["heroes"] == 1
    assert wb["meta"]["units"] == 0
    assert wb["meta"]["bows"] == 0
    assert wb["meta"]["throwingWeapons"] == 0
