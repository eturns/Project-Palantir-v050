"""Focused mechanical tests for Bert's 2024-profile Brutal Power Attack."""
import pytest
from three_trolls_roast_em_slowly import (
    BERT_PROFILE_ID,
    CAMPFIRE_RANGE_INCHES,
    RoastEmSlowlyContext,
    resolve_roast_em_slowly,
)


def context(**updates):
    args = dict(
        attacker_profile_id=BERT_PROFILE_ID,
        target_id="enemy-1",
        attacker_won_duel=True,
        target_is_enemy_in_combat=True,
        campfire_present=True,
        campfire_distance_inches=3.0,
    )
    args.update(updates)
    return RoastEmSlowlyContext(**args)


def test_success_sets_exact_effect_without_damage():
    result = resolve_roast_em_slowly(context())
    assert result.target_id == "enemy-1"
    assert result.replace_normal_strikes
    assert result.relocate_target_into_campfire_base_contact
    assert result.set_target_ablaze
    assert not result.damage_evaluated


def test_at_exactly_six_inches_is_eligible():
    assert resolve_roast_em_slowly(context(campfire_distance_inches=CAMPFIRE_RANGE_INCHES))


def test_over_six_inches_is_not_eligible():
    assert resolve_roast_em_slowly(context(campfire_distance_inches=6.01)) is None


@pytest.mark.parametrize("profile_id", ["TT_BILL", "TT_TOM", "OTHER"])
def test_only_bert_can_use_rule(profile_id):
    assert resolve_roast_em_slowly(context(attacker_profile_id=profile_id)) is None


def test_cannot_use_without_winning_duel():
    assert resolve_roast_em_slowly(context(attacker_won_duel=False)) is None


def test_must_target_an_enemy_in_same_combat():
    assert resolve_roast_em_slowly(context(target_is_enemy_in_combat=False)) is None


def test_requires_a_campfire():
    assert resolve_roast_em_slowly(context(campfire_present=False)) is None


def test_unknown_distance_does_not_infer_eligibility():
    assert resolve_roast_em_slowly(context(campfire_distance_inches=None)) is None


def test_cannot_combine_with_another_attack_replacement():
    assert resolve_roast_em_slowly(context(alternative_attack_already_used=True)) is None


@pytest.mark.parametrize("distance", [-1, float('nan'), float('inf'), True])
def test_rejects_invalid_distance(distance):
    with pytest.raises(ValueError):
        context(campfire_distance_inches=distance)


def test_zero_distance_is_valid():
    assert resolve_roast_em_slowly(context(campfire_distance_inches=0))


def test_result_does_not_mutate_input_context():
    original = context()
    _ = resolve_roast_em_slowly(original)
    assert original.campfire_distance_inches == 3.0
    assert original.attacker_won_duel


def test_no_external_battlefield_geometry_inferred():
    result = resolve_roast_em_slowly(context())
    assert not hasattr(result, "coordinates")
    assert not hasattr(result, "expected_wounds")
