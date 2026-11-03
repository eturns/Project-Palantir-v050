"""
Project Palantír
DEV-080-E2: Spell Versatility acceptance.

Author: Edward Turns (Project Lead)

Verifies real spell repertoire and category evidence
without inventing spell-effect scores.
"""

import pytest

from army import Army
from main import run_analysis_workflow
from magic_spell_versatility import (
    assess_magic_spell_versatility,
)


@pytest.fixture(scope="module")
def dol_guldur():
    return run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )


def test_real_necromancer_has_nine_spells(dol_guldur):
    result = assess_magic_spell_versatility(
        dol_guldur["army"]
    )

    assert result.distinct_spell_count == 9
    assert len(result.distinct_spell_ids) == 9
    assert "TRANSFIX" in result.distinct_spell_ids
    assert "CHILL_SOUL" in result.distinct_spell_ids


def test_real_spell_categories_are_preserved(dol_guldur):
    result = assess_magic_spell_versatility(
        dol_guldur["army"]
    )

    assert "CONTROL" in result.category_ids
    assert "OFFENCE" in result.category_ids

    categories = dict(result.category_spell_ids)

    assert "TRANSFIX" in categories["CONTROL"]
    assert "CHILL_SOUL" in categories["OFFENCE"]


def test_overlapping_tags_are_not_collapsed(dol_guldur):
    result = assess_magic_spell_versatility(
        dol_guldur["army"]
    )

    categories = dict(result.category_spell_ids)

    assert "DRAIN_COURAGE" in categories["COURAGE"]
    assert "DRAIN_COURAGE" in categories["CONTROL"]

    assert result.distinct_spell_count == 9


def test_two_casters_do_not_duplicate_spell_types(
    dol_guldur,
):
    source = next(
        model
        for model in dol_guldur["army"].fielded_models()
        if model.profile_id == "DG_NEC"
    )

    army = Army()
    army.add_configured_profile(
        source.configured_profile,
        quantity=2,
    )

    result = assess_magic_spell_versatility(army)

    assert result.distinct_spell_count == 9
    assert len(result.distinct_spell_ids) == 9


def test_empty_army_has_no_spell_versatility():
    result = assess_magic_spell_versatility(Army())

    assert result.distinct_spell_ids == ()
    assert result.distinct_spell_count == 0
    assert result.category_ids == ()
    assert result.unclassified_spell_ids == ()


def test_no_invented_impact_or_dashboard_score(dol_guldur):
    result = assess_magic_spell_versatility(
        dol_guldur["army"]
    )

    assert result.impact_score is None
    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "repertoire_verified_impact_not_quantified"
    )


def test_invalid_army_rejected():
    with pytest.raises(TypeError, match="Army"):
        assess_magic_spell_versatility(object())