"""G2-C3: Lethal Aim is explicit, mutually exclusive and single-shot only."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from defensive_state import DefensiveState
from ranged_weapon_profile import RangedWeaponProfile
from shooting_eligibility import ShootingContext
from lethal_aim_state import LethalAimState, LethalAimSpend
from hero_hunting_shooting import calculate_hero_hunting_shooting_evidence


def profile(*, rules=(), shoot="4+"):
    return SimpleNamespace(
        effective_wargear=(SimpleNamespace(id="WG_ORC_BOW", special_rules=()),),
        effective_special_rules=tuple(
            SimpleNamespace(rule=SimpleNamespace(id=rule)) for rule in rules
        ),
        effective_shooting=shoot,
        effective_defence=4,
        profile=SimpleNamespace(keywords=()),
    )


def calculate(*, rules=("LETHAL_AIM",), spend=None, state=None,
              attacks=1, in_way=()):
    attacker = profile(rules=rules)
    return calculate_hero_hunting_shooting_evidence(
        attacker=attacker, defender=profile(),
        weapon=RangedWeaponProfile("WG_ORC_BOW",18,2,attacks),
        defender_state=DefensiveState(1),
        context=ShootingContext(target_distance_inches=12),
        clear_line_of_sight=True,
        in_the_way_required_rolls=in_way,
        lethal_aim_state=state,
        lethal_aim_spend=spend,
    )


def test_explicit_spend_to_hit_improves_outcome():
    without = calculate(rules=())
    with_hit = calculate(spend=LethalAimSpend.TO_HIT, state=LethalAimState())
    assert with_hit.wound_probability_per_shot > without.wound_probability_per_shot


def test_explicit_spend_to_wound_improves_outcome():
    without = calculate(rules=())
    with_wound = calculate(spend=LethalAimSpend.TO_WOUND, state=LethalAimState())
    assert with_wound.wound_probability_per_shot > without.wound_probability_per_shot


def test_explicit_spend_in_the_way_improves_outcome():
    base = calculate(rules=(), in_way=(4,))
    improved = calculate(
        spend=LethalAimSpend.IN_THE_WAY, state=LethalAimState(), in_way=(4,)
    )
    assert improved.wound_probability_per_shot > base.wound_probability_per_shot


def test_no_implicit_lethal_aim_credit():
    with pytest.raises(ValueError, match="allocation must be explicit"):
        calculate()


def test_spent_free_might_fails_closed():
    with pytest.raises(ValueError, match="invalid Lethal Aim"):
        calculate(spend=LethalAimSpend.TO_WOUND,
                  state=LethalAimState(free_might_available=False))


def test_multiple_shot_spend_not_applied_to_every_shot():
    with pytest.raises(ValueError, match="across multiple shots"):
        calculate(spend=LethalAimSpend.TO_HIT, state=LethalAimState(), attacks=2)


def test_non_owner_may_not_spend_lethal_aim():
    with pytest.raises(ValueError, match="lacks Lethal Aim"):
        calculate(rules=(), spend=LethalAimSpend.TO_HIT, state=LethalAimState())
