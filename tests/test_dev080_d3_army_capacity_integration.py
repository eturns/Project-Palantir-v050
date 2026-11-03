"""
Project Palantír
DEV-080-D3: Army-level Casting Capacity acceptance.

Author: Edward Turns (Project Lead)

Verifies shared caster identities, effective starting
Will and rules-aware casting opportunity ceilings.
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
        m for m in imported["army"].fielded_models()
        if m.profile_id == "DG_NEC"
    )

    return model.configured_profile, imported["army_list"]


def make_army(necromancer_source, quantity=1, will=None):
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


def test_all_three_components_share_caster_id(necromancer_source):
    result = make_army(necromancer_source)

    effectiveness_ids = {
        model_id for model_id, _
        in result.caster_effectiveness
    }
    endurance_ids = {
        model_id for model_id, _
        in result.caster_endurance
    }
    capacity_ids = {
        model_id for model_id, _
        in result.caster_capacity
    }

    assert len(capacity_ids) == 1
    assert effectiveness_ids == endurance_ids == capacity_ids


def test_real_necromancer_capacity(necromancer_source):
    result = make_army(necromancer_source)

    assert len(result.caster_capacity) == 1

    _, capacity = result.caster_capacity[0]

    assert capacity.starting_will == 25
    assert capacity.distinct_spell_count == 9
    assert capacity.permitted_attempts_per_activation == 2
    assert capacity.opportunity_attempt_ceiling == 12
    assert capacity.modelled_attempt_ceiling == 12
    assert capacity.remaining_will_at_ceiling == 13


def test_two_casters_keep_separate_capacity(necromancer_source):
    result = make_army(
        necromancer_source,
        quantity=2,
    )

    assert len(result.caster_capacity) == 2

    ids = [
        model_id for model_id, _
        in result.caster_capacity
    ]
    assert len(set(ids)) == 2

    for _, capacity in result.caster_capacity:
        assert capacity.starting_will == 25
        assert capacity.modelled_attempt_ceiling == 12


def test_reduced_effective_will_limits_capacity(
    necromancer_source,
):
    result = make_army(necromancer_source, will=2)

    assert result.starting_caster_will == 2

    _, capacity = result.caster_capacity[0]

    assert capacity.starting_will == 2
    assert capacity.opportunity_attempt_ceiling == 12
    assert capacity.modelled_attempt_ceiling == 2
    assert capacity.remaining_will_at_ceiling == 0


def test_zero_will_excludes_funded_capacity(
    necromancer_source,
):
    result = make_army(necromancer_source, will=0)

    assert result.caster_effectiveness == ()
    assert result.caster_endurance == ()
    assert result.caster_capacity == ()


def test_capacity_remains_diagnostic(necromancer_source):
    result = make_army(necromancer_source)

    _, capacity = result.caster_capacity[0]

    assert capacity.dashboard_score is None
    assert capacity.scenario_score is None
    assert result.dashboard_score is None
    assert result.scenario_score is None
