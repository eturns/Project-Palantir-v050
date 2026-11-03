"""
Project Palantír
DEV-080-D3: Rules-aware Casting Capacity acceptance.

Author: Edward Turns (Project Lead)

Tests the real Rise of the Necromancer army
without inventing targets or battlefield events.
"""

import pytest

from main import run_analysis_workflow
from magic_caster_capacity import (
    assess_caster_capacity,
)


@pytest.fixture(scope="module")
def necromancer():
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    army = imported["army"]
    army_list = imported["army_list"]

    model = next(
        item for item in army.fielded_models()
        if item.profile_id == "DG_NEC"
    )

    return model.configured_profile, army, army_list


def assess(necromancer, will=25, activations=6):
    configured, army, army_list = necromancer

    return assess_caster_capacity(
        configured,
        army=army,
        army_list=army_list,
        remaining_will=will,
        hypothetical_activations=activations,
    )


def test_real_necromancer_has_nine_spells(necromancer):
    result = assess(necromancer)

    assert result.distinct_spell_count == 9
    assert result.starting_will == 25


def test_army_rule_grants_second_cast(necromancer):
    result = assess(necromancer)

    assert result.permitted_attempts_per_activation == 2
    assert result.spell_distinct_attempt_ceiling == 2
    assert result.opportunity_attempt_ceiling == 12
    assert result.modelled_attempt_ceiling == 12


def test_reduced_will_limits_capacity(necromancer):
    result = assess(necromancer, will=2)

    assert result.resource_attempt_ceiling == 2
    assert result.modelled_attempt_ceiling == 2
    assert result.remaining_will_at_ceiling == 0


def test_zero_will_prevents_funded_casting(necromancer):
    result = assess(necromancer, will=0)

    assert result.opportunity_attempt_ceiling == 12
    assert result.modelled_attempt_ceiling == 0
    assert result.remaining_will_at_ceiling == 0


def test_shorter_reference_window(necromancer):
    result = assess(necromancer, activations=3)

    assert result.hypothetical_activations == 3
    assert result.opportunity_attempt_ceiling == 6
    assert result.modelled_attempt_ceiling == 6


def test_no_calibrated_score(necromancer):
    result = assess(necromancer)

    assert result.evidence_status == (
        "conditional_capacity_ceiling"
    )
    assert result.dashboard_score is None
    assert result.scenario_score is None