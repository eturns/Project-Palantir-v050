"""
Project Palantír
DEV-080-F4D: Real-Army Casting Delivery Integration.

Author: Edward Turns (Project Lead)

Checks that provisional casting-delivery scores
derive from the real imported army assessments.

No production dashboard or calibration changes.
"""

import pytest

from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)
from army_magic_output_envelope import (
    assess_army_magic_output,
)
from magic_casting_delivery_score import (
    calculate_magic_casting_delivery,
)


@pytest.fixture(scope="module")
def reference_results():
    results = {}

    for name, fixture in (
        ("necromancer", "dol_guldur_700.json"),
        ("smaug", "smaug.json"),
        ("non_magic", "azogs-hunters.json"),
    ):
        imported = run_analysis_workflow(
            f"tests/fixtures/{fixture}",
            print_report=False,
        )

        magic = assess_army_magic_capability(
            imported["army"],
            imported["army_list"],
        )

        output = assess_army_magic_output(magic)

        delivery = calculate_magic_casting_delivery(
            expected_successes_lower=(
                output.minimum_expected_successes
            ),
            expected_successes_upper=(
                output.maximum_expected_successes
            ),
            modelled_attempts=output.modelled_attempts,
        )

        results[name] = delivery

    return results


def test_necromancer_delivery(reference_results):
    result = reference_results["necromancer"]

    assert result.lower_score == pytest.approx(5 / 9)
    assert result.upper_score == pytest.approx(8 / 9)


def test_smaug_delivery(reference_results):
    result = reference_results["smaug"]

    assert result.lower_score == pytest.approx(1 / 6)
    assert result.upper_score == pytest.approx(1 / 3)


def test_non_magic_delivery(reference_results):
    result = reference_results["non_magic"]

    assert result.lower_score == 0
    assert result.upper_score == 0


def test_reference_scores_are_ordered(reference_results):
    necromancer = reference_results["necromancer"]
    smaug = reference_results["smaug"]
    non_magic = reference_results["non_magic"]

    assert (
        necromancer.upper_score
        > smaug.upper_score
        > non_magic.upper_score
    )


def test_no_overall_magic_score_claimed(reference_results):
    for result in reference_results.values():
        assert result.dashboard_score is None
        assert result.scenario_score is None
        assert result.evidence_status == (
            "provisional_casting_delivery_only"
        )
