
"""
Project Palantír
DEV-080-C2: Magical Endurance acceptance tests.

Author: Edward Turns (Project Lead)

Uses real Dol Guldur spell data and explicit
hypothetical casting opportunities.
"""

import pytest

from main import run_analysis_workflow
from mechanical_magic_spell_profiles import (
    build_profile_magic_casting_evidence,
)
from magic_endurance_assessment import (
    assess_spell_endurance,
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

    return model.configured_profile, army, army_list


def make_evidence(necromancer, will):
    configured, army, army_list = necromancer

    return build_profile_magic_casting_evidence(
        configured,
        army=army,
        army_list=army_list,
        remaining_will=will,
    )


def assess(evidence, opportunities=6, enhanced=True):
    return assess_spell_endurance(
        evidence,
        spell_id="TRANSFIX",
        hypothetical_opportunities=opportunities,
        verified_rule_ids=(
            ("DG_HIS_SPIRIT",) if enhanced else ()
        ),
    )


def test_full_necromancer_endurance(necromancer):
    result = assess(make_evidence(necromancer, 25))

    assert result.starting_will == 25
    assert result.affordable_attempts == 25
    assert result.modelled_attempts == 6
    assert result.will_spent == 6
    assert result.remaining_will == 19

    assert result.probability_per_attempt == pytest.approx(
        8 / 9
    )
    assert result.expected_successful_casts == pytest.approx(
        16 / 3
    )


def test_two_will_limits_endurance(necromancer):
    result = assess(make_evidence(necromancer, 2))

    assert result.affordable_attempts == 2
    assert result.modelled_attempts == 2
    assert result.will_spent == 2
    assert result.remaining_will == 0
    assert result.expected_successful_casts == pytest.approx(
        16 / 9
    )


def test_zero_will_prevents_casting(necromancer):
    result = assess(make_evidence(necromancer, 0))

    assert result.affordable_attempts == 0
    assert result.modelled_attempts == 0
    assert result.will_spent == 0
    assert result.expected_successful_casts == 0


def test_bonus_die_improves_expected_successes(necromancer):
    evidence = make_evidence(necromancer, 25)

    normal = assess(evidence, enhanced=False)
    enhanced = assess(evidence, enhanced=True)

    assert normal.probability_per_attempt == pytest.approx(
        2 / 3
    )
    assert enhanced.probability_per_attempt == pytest.approx(
        8 / 9
    )
    assert enhanced.expected_successful_casts > (
        normal.expected_successful_casts
    )

    assert enhanced.will_spent == normal.will_spent


def test_opportunity_limit_is_respected(necromancer):
    result = assess(
        make_evidence(necromancer, 25),
        opportunities=3,
    )

    assert result.modelled_attempts == 3
    assert result.remaining_will == 22
    assert result.expected_successful_casts == pytest.approx(
        8 / 3
    )


def test_endurance_remains_uncalibrated(necromancer):
    result = assess(make_evidence(necromancer, 25))

    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == (
        "hypothetical_endurance_not_calibrated"
    )


def test_negative_opportunities_rejected(necromancer):
    evidence = make_evidence(necromancer, 25)

    with pytest.raises(ValueError, match="nonnegative"):
        assess(evidence, opportunities=-1)
