
"""
Project Palantír
DEV-080-C3: Per-caster Magical Endurance tests.

Author: Edward Turns (Project Lead)

Tests individual spell projections without assuming
that every spell is cast during the same engagement.
"""

import pytest

from main import run_analysis_workflow
from magic_caster_endurance import (
    assess_caster_endurance,
)


@pytest.fixture(scope="module")
def necromancer():
    result = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    army = result["army"]
    army_list = result["army_list"]

    model = next(
        model for model in army.fielded_models()
        if model.profile_id == "DG_NEC"
    )

    return model.configured_profile, army, army_list


def assess(necromancer, will=25, opportunities=6):
    configured, army, army_list = necromancer

    return assess_caster_endurance(
        configured,
        army=army,
        army_list=army_list,
        remaining_will=will,
        hypothetical_opportunities=opportunities,
    )


def test_nine_spell_projections(necromancer):
    result = assess(necromancer)

    assert result.profile_id == "DG_NEC"
    assert result.starting_will == 25
    assert len(result.spell_results) == 9

    spell_ids = [
        spell_id
        for spell_id, _ in result.spell_results
    ]

    assert len(set(spell_ids)) == 9


def test_each_spell_uses_independent_budget(necromancer):
    result = assess(necromancer)

    for _, spell in result.spell_results:
        assert spell.starting_will == 25
        assert spell.affordable_attempts == 25
        assert spell.modelled_attempts == 6
        assert spell.will_spent == 6
        assert spell.remaining_will == 19


def test_different_spells_retain_probabilities(necromancer):
    result = assess(necromancer)

    spells = dict(result.spell_results)

    assert spells["TRANSFIX"].probability_per_attempt == (
        pytest.approx(8 / 9)
    )

    assert spells["CHILL_SOUL"].probability_per_attempt == (
        pytest.approx(5 / 9)
    )

    assert (
        spells["TRANSFIX"].expected_successful_casts
        > spells["CHILL_SOUL"].expected_successful_casts
    )


def test_reduced_will_limits_all_alternatives(necromancer):
    result = assess(necromancer, will=2)

    assert result.starting_will == 2

    for _, spell in result.spell_results:
        assert spell.affordable_attempts == 2
        assert spell.modelled_attempts == 2
        assert spell.will_spent == 2
        assert spell.remaining_will == 0


def test_zero_will_has_no_funded_attempts(necromancer):
    result = assess(necromancer, will=0)

    for _, spell in result.spell_results:
        assert spell.modelled_attempts == 0
        assert spell.expected_successful_casts == 0


def test_no_premature_endurance_score(necromancer):
    result = assess(necromancer)

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "alternative_spell_endurance_projections"
    )