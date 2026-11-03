
"""
Project Palantír
DEV-080-B6: Casting effectiveness acceptance.

Author: Edward Turns (Project Lead)

Checks real-army casting probabilities without
altering calibration or scenario scoring.
"""

import pytest

from main import run_analysis_workflow
from magic_casting_effectiveness import (
    assess_caster_effectiveness,
)


@pytest.fixture(scope="module")
def necromancer():
    result = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    assert result is not None

    army = result["army"]
    army_list = result["army_list"]

    model = next(
        m for m in army.fielded_models()
        if m.profile_id == "DG_NEC"
    )

    return model, army, army_list


def test_nine_spells_identified(necromancer):
    model, army, army_list = necromancer

    result = assess_caster_effectiveness(
        model.configured_profile,
        army=army,
        army_list=army_list,
    )

    assert result.profile_id == "DG_NEC"
    assert result.spell_count == 9
    assert len(result.spell_results) == 9


def test_baseline_casting_average(necromancer):
    model, army, army_list = necromancer

    result = assess_caster_effectiveness(
        model.configured_profile,
        army=army,
        army_list=army_list,
    )

    assert result.baseline_probability == pytest.approx(
        14 / 27
    )


def test_enhanced_casting_average(necromancer):
    model, army, army_list = necromancer

    result = assess_caster_effectiveness(
        model.configured_profile,
        army=army,
        army_list=army_list,
    )

    assert result.enhanced_probability == pytest.approx(
        61 / 81
    )


def test_necromancer_special_rules(necromancer):
    model, army, army_list = necromancer

    result = assess_caster_effectiveness(
        model.configured_profile,
        army=army,
        army_list=army_list,
    )

    assert result.extra_casting_dice == 1
    assert result.additional_attempts_per_activation == 1


def test_no_calibrated_scores(necromancer):
    model, army, army_list = necromancer

    result = assess_caster_effectiveness(
        model.configured_profile,
        army=army,
        army_list=army_list,
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "conditional_casting_potential"
    )