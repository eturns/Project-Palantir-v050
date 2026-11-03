"""
Project Palantír
DEV-080-F2: Army Casting Output acceptance.

Author: Edward Turns (Project Lead)

Tests whole-army hypothetical casting output
with independent caster resources.
"""

import pytest

from army import Army
from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)
from army_magic_output_envelope import (
    assess_army_magic_output,
)


@pytest.fixture(scope="module")
def necromancer_source():
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    model = next(
        item for item in imported["army"].fielded_models()
        if item.profile_id == "DG_NEC"
    )

    return model.configured_profile, imported["army_list"]


def make_assessment(
    necromancer_source,
    quantity=1,
    will=None,
):
    configured, army_list = necromancer_source

    army = Army()
    army.add_configured_profile(
        configured,
        quantity=quantity,
    )

    if will is not None:
        army.entries[0].starting_resource_overrides = {
            "will": will
        }

    return assess_army_magic_capability(
        army, army_list
    )


def test_single_necromancer_output(necromancer_source):
    assessment = make_assessment(necromancer_source)

    result = assess_army_magic_output(assessment)

    assert result.caster_count == 1
    assert result.modelled_attempts == 12

    assert result.minimum_expected_successes == pytest.approx(
        20 / 3
    )
    assert result.maximum_expected_successes == pytest.approx(
        32 / 3
    )


def test_two_casters_retain_separate_results(
    necromancer_source,
):
    assessment = make_assessment(
        necromancer_source,
        quantity=2,
    )

    result = assess_army_magic_output(assessment)

    assert result.caster_count == 2
    assert result.modelled_attempts == 24
    assert len(result.caster_results) == 2

    ids = [
        model_id
        for model_id, _ in result.caster_results
    ]

    assert len(set(ids)) == 2

    assert result.maximum_expected_successes == pytest.approx(
        64 / 3
    )


def test_reduced_will_limits_individual_output(
    necromancer_source,
):
    assessment = make_assessment(
        necromancer_source,
        will=2,
    )

    result = assess_army_magic_output(assessment)

    assert result.modelled_attempts == 2
    assert result.maximum_expected_successes == pytest.approx(
        16 / 9
    )


def test_zero_will_has_no_funded_output(
    necromancer_source,
):
    assessment = make_assessment(
        necromancer_source,
        will=0,
    )

    result = assess_army_magic_output(assessment)

    assert result.caster_count == 0
    assert result.modelled_attempts == 0
    assert result.minimum_expected_successes == 0
    assert result.maximum_expected_successes == 0


def test_empty_army_has_zero_output(necromancer_source):
    _, army_list = necromancer_source

    assessment = assess_army_magic_capability(
        Army(), army_list
    )

    result = assess_army_magic_output(assessment)

    assert result.caster_count == 0
    assert result.caster_results == ()
    assert result.modelled_attempts == 0
    assert result.maximum_expected_successes == 0


def test_output_remains_uncalibrated(necromancer_source):
    assessment = make_assessment(necromancer_source)

    result = assess_army_magic_output(assessment)

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "conditional_army_casting_output"
    )