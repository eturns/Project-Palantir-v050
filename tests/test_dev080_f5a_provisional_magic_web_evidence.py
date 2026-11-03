"""
Project Palantír
DEV-080-F5A: Provisional Web Magic Evidence Tests.

Author: Edward Turns (Project Lead)

Validates the JSON-compatible Magic presentation
contract using real imported armies.

No dashboard calibration or scenario changes.
"""

import json

import pytest

from main import run_analysis_workflow
from provisional_magic_web_evidence import (
    build_provisional_magic_web_evidence,
)


@pytest.fixture(scope="module")
def reference_evidence():
    results = {}

    for name, filename in (
        ("necromancer", "dol_guldur_700.json"),
        ("smaug", "smaug.json"),
        ("non_magic", "azogs-hunters.json"),
    ):
        workflow = run_analysis_workflow(
            f"tests/fixtures/{filename}",
            print_report=False,
        )

        results[name] = (
            build_provisional_magic_web_evidence(
                workflow
            )
        )

    return results


def test_necromancer_casting_delivery(reference_evidence):
    result = reference_evidence["necromancer"]

    assert result["caster_count"] == 1
    assert result["distinct_spell_count"] == 9
    assert result["modelled_attempts"] == 12

    assert result["lower_score"] == pytest.approx(
        5 / 9
    )
    assert result["upper_score"] == pytest.approx(
        8 / 9
    )


def test_smaug_temporary_will(reference_evidence):
    result = reference_evidence["smaug"]

    assert result["caster_count"] == 1
    assert result["modelled_attempts"] == 6
    assert result["funded_attempts"] == 6

    assert result["temporary_will_spent"] == 6
    assert result["permanent_will_spent"] == 0
    assert result["permanent_will_remaining"] == 6

    assert result["lower_score"] == pytest.approx(
        1 / 6
    )
    assert result["upper_score"] == pytest.approx(
        1 / 3
    )


def test_smaug_unverified_effect_visible(reference_evidence):
    result = reference_evidence["smaug"]

    assert "FOIL_MAGIC" in result[
        "unverified_effect_spell_ids"
    ]


def test_non_magic_army_has_zero_delivery(
    reference_evidence,
):
    result = reference_evidence["non_magic"]

    assert result["caster_count"] == 0
    assert result["modelled_attempts"] == 0
    assert result["lower_score"] == 0
    assert result["upper_score"] == 0
    assert result["spell_ids"] == []


def test_all_results_are_json_serializable(
    reference_evidence,
):
    for result in reference_evidence.values():
        encoded = json.dumps(
            result,
            allow_nan=False,
        )

        decoded = json.loads(encoded)

        assert decoded == result
        assert decoded["display_only"] is True


def test_overall_magic_remains_unrated(
    reference_evidence,
):
    for result in reference_evidence.values():
        assert result["overall_magic_score"] is None
        assert result["status"] == (
            "provisional_casting_delivery_only"
        )
        assert result["reference_attempts"] == 12
        assert result["reference_activations"] == 6