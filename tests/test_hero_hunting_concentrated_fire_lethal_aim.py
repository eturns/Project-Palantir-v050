"""G2-C5B: per-shot Lethal Aim plus standard archers and shared target Fate."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from defensive_state import DefensiveState
from hero_hunting_concentrated_fire import FocusedShooter, calculate_concentrated_fire_evidence
from hero_hunting_lethal_aim_volley import calculate_lethal_aim_volley_evidence
from lethal_aim_state import LethalAimState, LethalAimSpend
from ranged_weapon_profile import RangedWeaponProfile
from shooting_eligibility import ShootingContext


def model(rules=()):
    return SimpleNamespace(
        effective_wargear=(SimpleNamespace(id="WG_ORC_BOW", special_rules=()),),
        effective_special_rules=tuple(SimpleNamespace(rule=SimpleNamespace(id=r)) for r in rules),
        effective_shooting="4+", effective_defence=4,
        profile=SimpleNamespace(keywords=()),
    )


def entry(name, rules=(), spend=None, shot=None, state=None, distance=12):
    return FocusedShooter(
        shooter_id=name, attacker=model(rules),
        weapon=RangedWeaponProfile("WG_ORC_BOW", 18, 2, 1),
        context=ShootingContext(target_distance_inches=distance),
        clear_line_of_sight=True,
        lethal_aim_spend=spend,
        lethal_aim_shot_index=shot,
        lethal_aim_state=state,
    )


def calculate(*shooters, fate=0):
    return calculate_concentrated_fire_evidence(
        shooters=shooters, defender=model(),
        defender_state=DefensiveState(1, remaining_fate=fate),
    )


def test_narzug_two_shots_and_one_archer_three_total():
    result = calculate(entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                             LethalAimSpend.TO_WOUND, 0, LethalAimState()),
                       entry("archer"))
    assert result.total_shots == 3
    assert result.shooter_count == 2
    assert len(result.incoming_wound_distribution) == 4
    assert sum(result.incoming_wound_distribution) == 1


def test_aggregates_exact_c5a_volley_distribution_with_archer():
    narzug = entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                   LethalAimSpend.TO_HIT, 1, LethalAimState())
    solo = calculate_lethal_aim_volley_evidence(
        attacker=narzug.attacker, defender=model(), weapon=narzug.weapon,
        defender_state=DefensiveState(1), context=narzug.context,
        clear_line_of_sight=True, lethal_aim_state=narzug.lethal_aim_state,
        lethal_aim_spend=narzug.lethal_aim_spend,
        lethal_aim_shot_index=narzug.lethal_aim_shot_index,
    )
    result = calculate(narzug, entry("archer"))
    assert result.expected_wounds > solo.expected_wounds
    assert result.elimination_probability >= solo.elimination_probability
    assert result.incoming_wound_distribution != solo.incoming_wound_distribution


def test_fate_is_not_reset_for_each_shooter():
    shooters = (entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                      LethalAimSpend.TO_WOUND, 0, LethalAimState()),
                entry("archer"))
    without = calculate(*shooters)
    with_fate = calculate(*shooters, fate=1)
    assert with_fate.elimination_probability < without.elimination_probability
    assert with_fate.incoming_wound_distribution == without.incoming_wound_distribution


@pytest.mark.parametrize("spend,shot,state", [
    (None,None,None),
    (LethalAimSpend.TO_HIT,None,LethalAimState()),
    (LethalAimSpend.TO_HIT,0,None),
])
def test_missing_allocation_fails_closed(spend, shot, state):
    with pytest.raises(ValueError, match="allocation required"):
        calculate(entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"), spend, shot, state))


def test_spent_might_fails_closed():
    with pytest.raises(ValueError, match="invalid Lethal Aim"):
        calculate(entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                        LethalAimSpend.TO_HIT, 0, LethalAimState(False)))


def test_out_of_range_does_not_contribute():
    with pytest.raises(ValueError, match="cannot fire"):
        calculate(entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                        LethalAimSpend.TO_WOUND, 0, LethalAimState(), distance=19))


def test_invalid_shot_index_fails_closed():
    with pytest.raises(ValueError, match="shot index"):
        calculate(entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                        LethalAimSpend.TO_HIT, 2, LethalAimState()))


def test_non_owner_allocation_fails_closed():
    with pytest.raises(ValueError, match="non-Lethal Aim"):
        calculate(entry("archer", spend=LethalAimSpend.TO_HIT,
                        shot=0, state=LethalAimState()))


def test_duplicate_shooter_still_rejected():
    with pytest.raises(ValueError, match="duplicated shooter identity"):
        calculate(entry("same"), entry("same"))


def test_cavalry_context_for_lethal_aim_rejected_not_ignored():
    narzug = entry("narzug", ("LETHAL_AIM", "EXPERT_SHOT"),
                   LethalAimSpend.TO_HIT, 0, LethalAimState())
    from dataclasses import replace
    with pytest.raises(ValueError, match="cavalry context unsupported"):
        calculate(replace(narzug, target_is_cavalry=True))
