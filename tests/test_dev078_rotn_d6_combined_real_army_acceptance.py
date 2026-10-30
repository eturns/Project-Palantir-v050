"""DEV-078-ROTN-D6: integrated Rise real-army acceptance.

Author: Edward Turns (Project Lead)

Test-only closure gate. Uses the existing production importer, canonical army
rules, and D4/D5 service entrypoint. No fabricated battlefield rolls and no
changes to calibration or the scoring pipeline.
"""

import pytest

from necromancer_free_will_casting import FundedCastRequest
from rotn_army_resistance_outcomes_service import ResistanceRequest
from tests.test_dev078_rotn_d4_production_integration import rise, call, nec_id


def funded(spell, enemy, spent=1):
    return FundedCastRequest(
        spell_id=spell, target_id=enemy, cast_value=4, will_spent=spent,
    )


def combined_requests(rise):
    nec = nec_id(rise)
    return {
        "rotn_funded_cast_requests_by_model_id": {
            nec: (funded("TRANSFIX", "enemy-a"), funded("COMPEL", "enemy-b"))
        },
        "rotn_resistance_requests_by_model_id": {
            nec: ResistanceRequest(cast_highest=4, will_available=2,
                                   will_spent=1, hero=True),
        },
    }


def test_real_army_rule_and_fielded_model_entitlement(rise):
    result = call(rise)
    inventory = result["mechanical_army_magic_resistance"]
    assert inventory.source_rule_id == "DG_POWER_OF_THE_NECROMANCER"
    assert inventory.model_count == len(rise[0].fielded_models())
    assert set(inventory.eligible_model_ids) == {
        m.id for m in rise[0].fielded_models()
    }
    assert nec_id(rise) in result["mechanical_necromancer_cast_sequence"].eligible_model_ids


def test_combined_cast_and_resistance_exposed_by_same_service_call(rise):
    result = call(rise, **combined_requests(rise))
    assert "mechanical_necromancer_cast_sequence" in result
    assert "mechanical_army_magic_resistance" in result
    assert "mechanical_army_resistance_outcomes" in result
    assert result["mechanical_necromancer_cast_sequence"].rule_id == "DG_POWER_OF_THE_NECROMANCER"
    assert result["mechanical_army_resistance_outcomes"].source_rule_id == "DG_POWER_OF_THE_NECROMANCER"


def test_two_casts_each_gain_one_free_die_and_share_will_ledger(rise):
    report = call(rise, **combined_requests(rise))["mechanical_necromancer_cast_sequence"]
    model_id, sequence = report.funded_sequences[0]
    assert model_id == nec_id(rise)
    assert report.permitted_attempts_per_activation == 2
    assert len(sequence.casts) == 2
    assert [c.cast.will_spent for c in sequence.casts] == [1, 1]
    assert [c.cast.additional_dice for c in sequence.casts] == [1, 1]
    assert [c.cast.dice_total for c in sequence.casts] == [2, 2]
    assert sequence.casts[0].will_after == sequence.casts[1].will_before
    assert sequence.remaining_will == sequence.initial_will - 2


def test_resistance_accounts_for_free_die_without_spending_it(rise):
    report = call(rise, **combined_requests(rise))["mechanical_army_resistance_outcomes"]
    model_id, outcome = report.outcomes_by_model_id[0]
    assert model_id == nec_id(rise)
    assert outcome.will_spent == 1
    assert outcome.free_dice == 1
    assert outcome.dice_total == 2
    assert outcome.will_after_spend == 1
    assert outcome.probability_resisted == pytest.approx(0.75)
    assert outcome.expected_hero_will_refund == pytest.approx(1 / 6)


def test_free_resistance_die_when_target_has_no_will(rise):
    nec = nec_id(rise)
    result = call(rise, rotn_resistance_requests_by_model_id={
        nec: ResistanceRequest(cast_highest=6, will_available=0, hero=True)
    })
    outcome = result["mechanical_army_resistance_outcomes"].outcomes_by_model_id[0][1]
    assert outcome.will_after_spend == 0
    assert outcome.dice_total == 1
    assert outcome.probability_resisted == pytest.approx(1 / 6)
    assert outcome.expected_hero_will_refund == 0


def test_combined_evidence_cannot_change_scoring(rise):
    baseline = call(rise)
    combined = call(rise, **combined_requests(rise))
    for key in ("metrics", "metric_densities", "metric_assessments", "battlefield_assessments"):
        assert combined[key] == baseline[key], key
    assert combined["validation_errors"] == baseline["validation_errors"]
    assert "mechanical_army_resistance_outcomes" not in baseline


def test_combined_evidence_is_uncalibrated(rise):
    result = call(rise, **combined_requests(rise))
    for key in ("mechanical_necromancer_cast_sequence", "mechanical_army_magic_resistance",
                "mechanical_army_resistance_outcomes"):
        assert result[key].dashboard_score is None
        assert result[key].scenario_score is None


def test_duplicate_target_rejected_when_resistance_also_requested(rise):
    nec = nec_id(rise)
    with pytest.raises(ValueError, match="same enemy"):
        call(rise,
             rotn_funded_cast_requests_by_model_id={
                 nec: (funded("TRANSFIX", "enemy-a"), funded("COMPEL", "enemy-a"))
             },
             rotn_resistance_requests_by_model_id={
                 nec: ResistanceRequest(cast_highest=4, will_available=0)
             })


def test_unknown_resistance_target_rejected_when_casting_requested(rise):
    nec = nec_id(rise)
    with pytest.raises(ValueError, match="not fielded"):
        call(rise,
             rotn_funded_cast_requests_by_model_id={nec: (funded("TRANSFIX", "enemy-a"),)},
             rotn_resistance_requests_by_model_id={
                 "not-fielded": ResistanceRequest(cast_highest=4, will_available=0)
             })
