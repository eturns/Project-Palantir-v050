
"""
Project Palantír
DEV-080-C3: Army-level Magical Endurance integration.

Author: Edward Turns (Project Lead)

Verify caster identities, individual Will budgets
and diagnostic-only assessment behaviour.
"""

import pytest

from army import Army
from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
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


def test_real_army_caster_identity_matches(necromancer_source):
    configured, army_list = necromancer_source

    army = Army()
    army.add_configured_profile(configured)

    result = assess_army_magic_capability(
        army, army_list
    )

    effectiveness_ids = {
        model_id
        for model_id, _ in result.caster_effectiveness
    }

    endurance_ids = {
        model_id
        for model_id, _ in result.caster_endurance
    }

    assert len(effectiveness_ids) == 1
    assert effectiveness_ids == endurance_ids


def test_two_casters_have_separate_endurance(necromancer_source):
    configured, army_list = necromancer_source

    army = Army()
    army.add_configured_profile(
        configured,
        quantity=2,
    )

    result = assess_army_magic_capability(
        army, army_list
    )

    assert len(result.caster_endurance) == 2

    ids = [model_id for model_id, _ in result.caster_endurance]
    assert len(set(ids)) == 2

    for _, endurance in result.caster_endurance:
        assert endurance.starting_will == 25
        assert len(endurance.spell_results) == 9


def test_effective_will_override_reaches_endurance(
    necromancer_source,
):
    configured, army_list = necromancer_source

    army = Army()
    army.add_configured_profile(configured)

    army.entries[0].starting_resource_overrides = {
        "will": 2
    }

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.starting_caster_will == 2
    assert len(result.caster_endurance) == 1

    _, endurance = result.caster_endurance[0]

    assert endurance.starting_will == 2

    for _, spell in endurance.spell_results:
        assert spell.modelled_attempts == 2
        assert spell.will_spent == 2
        assert spell.remaining_will == 0


def test_zero_will_excludes_funded_endurance(
    necromancer_source,
):
    configured, army_list = necromancer_source

    army = Army()
    army.add_configured_profile(configured)

    army.entries[0].starting_resource_overrides = {
        "will": 0
    }

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.starting_caster_will == 0
    assert result.caster_effectiveness == ()
    assert result.caster_endurance == ()


def test_no_calibrated_army_score(necromancer_source):
    configured, army_list = necromancer_source

    army = Army()
    army.add_configured_profile(configured)

    result = assess_army_magic_capability(
        army, army_list
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None

    _, endurance = result.caster_endurance[0]

    assert endurance.dashboard_score is None
    assert endurance.scenario_score is None