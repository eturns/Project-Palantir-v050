"""
Project Palantír
DEV-080-E3: Spell Impact coverage acceptance.

Author: Edward Turns (Project Lead)

Verifies existing mechanical effect function coverage
without inferring battlefield advantage or scores.
"""

import pytest

from main import run_analysis_workflow
from magic_spell_versatility import (
    assess_magic_spell_versatility,
)
from magic_spell_impact_coverage import (
    assess_spell_impact_coverage,
)


@pytest.fixture(scope="module")
def necromancer_spells():
    imported = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    versatility = assess_magic_spell_versatility(
        imported["army"]
    )

    return versatility.distinct_spell_ids


def test_all_nine_necromancer_spells_have_effect_functions(
    necromancer_spells,
):
    result = assess_spell_impact_coverage(
        necromancer_spells
    )

    assert len(result.distinct_spell_ids) == 9
    assert len(result.verified_effect_spell_ids) == 9
    assert result.unverified_effect_spell_ids == ()


def test_transfix_and_chill_soul_use_correct_functions(
    necromancer_spells,
):
    result = assess_spell_impact_coverage(
        necromancer_spells
    )

    functions = dict(
        result.verified_effect_function_names
    )

    assert functions["TRANSFIX"] == (
        "calculate_transfix_hero_hunting"
    )
    assert functions["CHILL_SOUL"] == (
        "calculate_chill_soul_hero_hunting"
    )


def test_unknown_spell_remains_unverified():
    result = assess_spell_impact_coverage(
        ("UNKNOWN_SPELL",)
    )

    assert result.verified_effect_spell_ids == ()
    assert result.unverified_effect_spell_ids == (
        "UNKNOWN_SPELL",
    )
    assert result.impact_score is None


def test_duplicates_do_not_inflate_coverage():
    result = assess_spell_impact_coverage(
        ("TRANSFIX", "TRANSFIX", "CHILL_SOUL")
    )

    assert result.distinct_spell_ids == (
        "CHILL_SOUL",
        "TRANSFIX",
    )
    assert len(result.verified_effect_spell_ids) == 2


def test_empty_spell_list_has_no_impact():
    result = assess_spell_impact_coverage(())

    assert result.distinct_spell_ids == ()
    assert result.verified_effect_spell_ids == ()
    assert result.unverified_effect_spell_ids == ()
    assert result.impact_score is None


def test_coverage_does_not_imply_battlefield_impact(
    necromancer_spells,
):
    result = assess_spell_impact_coverage(
        necromancer_spells
    )

    assert result.impact_score is None
    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "rules_backed_functions_available_impact_unresolved"
    )


def test_invalid_input_rejected():
    with pytest.raises(TypeError):
        assess_spell_impact_coverage(
            ["TRANSFIX"]
        )
