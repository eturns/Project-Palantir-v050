
"""
Project Palantír
DEV-080-B5: Army-level Magic capability acceptance.

Author: Edward Turns (Project Lead)
"""

from types import SimpleNamespace

import pytest

from army import Army
from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)


@pytest.fixture(scope="module")
def dol_guldur():
    result = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    assert result is not None
    return result["army"], result["army_list"]


def test_real_dol_guldur_magic_inventory(dol_guldur):
    army, army_list = dol_guldur

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.caster_count == 1
    assert result.starting_caster_will == 25
    assert len(result.distinct_spell_ids) == 9
    assert "TRANSFIX" in result.distinct_spell_ids


def test_real_necromancer_casting_entitlement(dol_guldur):
    army, army_list = dol_guldur

    result = assess_army_magic_capability(
        army, army_list
    )

    assert len(result.enhanced_casting_model_ids) == 1
    assert result.enhanced_attempts_per_activation == 2


def test_army_magic_resources_remain_separate(dol_guldur):
    army, army_list = dol_guldur

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.one_will_attempt_ceiling == 25
    assert result.one_will_probability_weighted_mean == (
        pytest.approx(0.5185185185185185)
    )


def test_empty_army_has_no_invented_magic():
    army = Army()

    army_list = SimpleNamespace(
        id="EMPTY_TEST_ARMY",
        army_rules=(),
    )

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.caster_count == 0
    assert result.starting_caster_will == 0
    assert result.distinct_spell_ids == ()
    assert result.one_will_probability_weighted_mean is None
    assert result.enhanced_casting_model_ids == ()
    assert result.enhanced_attempts_per_activation is None


def test_army_assessment_does_not_create_scores(
    dol_guldur,
):
    army, army_list = dol_guldur

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "roster_potential_not_calibrated"
    )

def test_army_contains_real_caster_effectiveness(dol_guldur):
    """Verify the army report exposes real caster measurements."""
    army, army_list = dol_guldur

    result = assess_army_magic_capability(
        army, army_list
    )

    assert len(result.caster_effectiveness) == 1

    model_id, casting = result.caster_effectiveness[0]

    assert model_id
    assert casting.profile_id == "DG_NEC"
    assert casting.spell_count == 9

    assert casting.baseline_probability == pytest.approx(
        14 / 27
    )

    assert casting.enhanced_probability == pytest.approx(
        61 / 81
    )

    assert casting.extra_casting_dice == 1
    assert casting.additional_attempts_per_activation == 1

    assert casting.dashboard_score is None
    assert casting.scenario_score is None
