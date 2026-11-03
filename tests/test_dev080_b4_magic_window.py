
"""
Project Palantír
DEV-080-B4: Real-army Magic casting window.

Author: Edward Turns (Project Lead)
"""

import pytest

from main import run_analysis_workflow
from mechanical_magic_spell_profiles import (
    build_profile_magic_casting_evidence,
)
from magic_capability_measurement import (
    measure_magic_casting_potential,
)
from necromancer_free_will_casting import (
    FundedCastRequest,
    assess_necromancer_funded_casts,
)


@pytest.fixture(scope="module")
def necromancer_data():
    result = run_analysis_workflow(
        "tests/fixtures/dol_guldur_700.json",
        print_report=False,
    )

    army = result["army"]
    army_list = result["army_list"]

    nec = next(
        model for model in army.fielded_models()
        if model.profile_id == "DG_NEC"
    )

    evidence = build_profile_magic_casting_evidence(
        nec.configured_profile,
        army=army,
        army_list=army_list,
    )

    rules = tuple(
        rule.id for rule in army_list.army_rules
    )

    return evidence, rules


def make_request(evidence, spell_id, target):
    option = next(
        item for item in evidence.spell_options
        if item.spell_id == spell_id
        and not item.conditional_rule_ids
    )

    return FundedCastRequest(
        spell_id=spell_id,
        target_id=target,
        cast_value=option.cast_value,
        will_spent=1,
    )


def test_two_spells_share_will_budget(necromancer_data):
    evidence, rules = necromancer_data

    requests = (
        make_request(evidence, "TRANSFIX", "enemy-1"),
        make_request(evidence, "COMPEL", "enemy-2"),
    )

    sequence = assess_necromancer_funded_casts(
        profile_id="DG_NEC",
        active_army_rule_ids=rules,
        initial_will=evidence.will_available,
        requests=requests,
    )

    assert len(sequence.casts) == 2
    assert sequence.remaining_will == evidence.will_available - 2

    assert all(
        cast.cast.additional_dice == 1
        for cast in sequence.casts
    )

    assert all(
        cast.cast.will_spent == 1
        for cast in sequence.casts
    )


def test_measurements_match_sequence(necromancer_data):
    evidence, rules = necromancer_data

    requests = (
        make_request(evidence, "TRANSFIX", "enemy-1"),
        make_request(evidence, "COMPEL", "enemy-2"),
    )

    sequence = assess_necromancer_funded_casts(
        profile_id="DG_NEC",
        active_army_rule_ids=rules,
        initial_will=evidence.will_available,
        requests=requests,
    )

    for request, cast in zip(requests, sequence.casts):
        measurement = measure_magic_casting_potential(
            evidence,
            spell_id=request.spell_id,
            verified_rule_ids=("DG_HIS_SPIRIT",),
        )

        assert measurement.casting_probability == pytest.approx(
            cast.cast.probability
        )
        assert measurement.additional_dice == cast.cast.additional_dice


def test_duplicate_target_rejected(necromancer_data):
    evidence, rules = necromancer_data

    requests = (
        make_request(evidence, "TRANSFIX", "enemy-1"),
        make_request(evidence, "COMPEL", "enemy-1"),
    )

    with pytest.raises(ValueError, match="same enemy"):
        assess_necromancer_funded_casts(
            profile_id="DG_NEC",
            active_army_rule_ids=rules,
            initial_will=evidence.will_available,
            requests=requests,
        )
