"""
Project Palantír
DEV-080-E4: Complete Magic assessment acceptance.

Author: Edward Turns (Project Lead)

Verifies four-component army evidence without
introducing uncalibrated Magic scores.
"""

import pytest

from army import Army
from main import run_analysis_workflow
from army_magic_capability_assessment import (
    assess_army_magic_capability,
)


@pytest.fixture(scope="module")
def dol_guldur():
    return run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )


def test_four_components_present(dol_guldur):
    result = assess_army_magic_capability(
        dol_guldur["army"],
        dol_guldur["army_list"],
    )

    assert len(result.caster_effectiveness) == 1
    assert len(result.caster_endurance) == 1
    assert len(result.caster_capacity) == 1

    assert result.spell_versatility.distinct_spell_count == 9
    assert len(
        result.spell_impact_coverage.verified_effect_spell_ids
    ) == 9


def test_three_caster_components_share_identity(dol_guldur):
    result = assess_army_magic_capability(
        dol_guldur["army"],
        dol_guldur["army_list"],
    )

    ids = [
        result.caster_effectiveness[0][0],
        result.caster_endurance[0][0],
        result.caster_capacity[0][0],
    ]

    assert len(set(ids)) == 1


def test_components_share_resource_budget(dol_guldur):
    result = assess_army_magic_capability(
        dol_guldur["army"],
        dol_guldur["army_list"],
    )

    _, endurance = result.caster_endurance[0]
    _, capacity = result.caster_capacity[0]

    assert result.starting_caster_will == 25
    assert endurance.starting_will == 25
    assert capacity.starting_will == 25

    # Endurance and capacity use different
    # hypothetical opportunity assumptions.
    assert endurance.hypothetical_opportunities == 6
    assert capacity.hypothetical_activations == 6

    assert capacity.modelled_attempt_ceiling == 12


def test_versatility_does_not_become_impact_score(dol_guldur):
    result = assess_army_magic_capability(
        dol_guldur["army"],
        dol_guldur["army_list"],
    )

    assert result.spell_versatility.impact_score is None
    assert result.spell_impact_coverage.impact_score is None

    assert result.dashboard_score is None
    assert result.scenario_score is None


def test_zero_will_retains_repertoire_but_no_funded_casts(
    dol_guldur,
):
    source = next(
        model
        for model in dol_guldur["army"].fielded_models()
        if model.profile_id == "DG_NEC"
    )

    army = Army()
    army.add_configured_profile(source.configured_profile)
    army.entries[0].starting_resource_overrides = {
        "will": 0
    }

    result = assess_army_magic_capability(
        army,
        dol_guldur["army_list"],
    )

    assert result.caster_effectiveness == ()
    assert result.caster_endurance == ()
    assert result.caster_capacity == ()

    # Known spells remain in the repertoire,
    # even with no funded casting available.
    assert result.spell_versatility.distinct_spell_count == 9
    assert result.spell_impact_coverage.impact_score is None