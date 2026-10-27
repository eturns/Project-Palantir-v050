"""DEV-077-TT-D2D: test Tom's conditional S6-area Brutal Power Attack."""
from dataclasses import replace
from fractions import Fraction
import pytest

from three_trolls_squash_em_into_jelly import (
    SquashContext, SquashTarget, SquashHit, TOM_PROFILE_ID,
    SQUASH_STRENGTH, resolve_squash_em_into_jelly,
)
from wound_table import get_wound_target
from wound_probability import get_wound_probability


def context(*targets, **kwargs):
    arguments = dict(attacker_profile_id=TOM_PROFILE_ID,
                     attacker_won_duel=True,
                     engaged_enemies=tuple(SquashTarget(name, defence)
                                           for name, defence in targets))
    arguments.update(kwargs)
    return SquashContext(**arguments)


def test_one_hit_for_one_engaged_enemy():
    result = resolve_squash_em_into_jelly(context(("enemy", 6)))
    assert len(result.hits) == 1
    assert result.hits[0].target_id == "enemy"
    assert result.hits[0].strength == 6


def test_each_engaged_enemy_receives_exactly_one_hit():
    result = resolve_squash_em_into_jelly(context(("a", 3), ("b", 6), ("c", 10)))
    assert [hit.target_id for hit in result.hits] == ["a", "b", "c"]
    assert len(result.hits) == 3


@pytest.mark.parametrize("defence", range(1, 11))
def test_wound_probability_uses_existing_wound_table(defence):
    result = resolve_squash_em_into_jelly(context(("one", defence)))
    assert result.hits[0].wound_probability == get_wound_probability(
        get_wound_target(strength=6, defence=defence)
    )


def test_replaces_strikes():
    assert resolve_squash_em_into_jelly(context(("a", 5))).replaces_normal_strikes


def test_only_survivors_may_be_knocked_prone():
    result = resolve_squash_em_into_jelly(context(("a", 5)))
    assert result.hits[0].knock_prone_if_survives
    assert not hasattr(result.hits[0], "is_prone")


def test_no_unsupported_actual_damage_claim():
    assert not resolve_squash_em_into_jelly(context(("a", 5))).actual_damage_evaluated


def test_expected_unsaved_wounds_sums_individual_probabilities():
    result = resolve_squash_em_into_jelly(context(("a", 5), ("b", 9)))
    assert result.expected_wounds_before_saves == sum(
        (hit.wound_probability for hit in result.hits), Fraction(0, 1))


@pytest.mark.parametrize("change", [
    {"attacker_profile_id": "TT_BILL"},
    {"attacker_won_duel": False},
    {"alternative_attack_already_used": True},
    {"engaged_enemies": ()},
])
def test_not_available_if_prerequisite_missing(change):
    assert resolve_squash_em_into_jelly(replace(context(("a", 5)), **change)) is None


@pytest.mark.parametrize("defence", [0, -1, 11, True, 5.5])
def test_reject_invalid_defence(defence):
    with pytest.raises(ValueError):
        SquashTarget("a", defence)


def test_reject_duplicate_target_ids():
    with pytest.raises(ValueError):
        context(("a", 5), ("a", 6))


def test_reject_blank_target_id():
    with pytest.raises(ValueError):
        SquashTarget(" ", 5)


def test_reject_bad_attacker_id():
    with pytest.raises(ValueError):
        context(("a", 5), attacker_profile_id="")


def test_reject_non_boolean_duel_status():
    with pytest.raises(ValueError):
        context(("a", 5), attacker_won_duel=1)


def test_reject_non_boolean_alternative_attack():
    with pytest.raises(ValueError):
        context(("a", 5), alternative_attack_already_used=1)


def test_reject_non_target_entries():
    with pytest.raises(ValueError):
        SquashContext(TOM_PROFILE_ID, True, ("enemy",))


def test_reject_non_tuple_targets():
    with pytest.raises(ValueError):
        SquashContext(TOM_PROFILE_ID, True, [SquashTarget("a", 5)])


def test_profile_and_strength_constants():
    assert TOM_PROFILE_ID == "TT_TOM"
    assert SQUASH_STRENGTH == 6
