"""C5A isolated per-shot free-Might allocation tests."""
from fractions import Fraction
from types import SimpleNamespace
import pytest
from defensive_state import DefensiveState
from hero_hunting_lethal_aim_volley import calculate_lethal_aim_volley_evidence
from lethal_aim_state import LethalAimSpend, LethalAimState
from ranged_weapon_profile import RangedWeaponProfile
from shooting_eligibility import ShootingContext
from shooting_wound_probability import get_shooting_wound_probability


def model(*, rules=(), shoot='4+', defence=4):
    return SimpleNamespace(
        effective_wargear=(SimpleNamespace(id='WG_ORC_BOW', special_rules=()),),
        effective_special_rules=tuple(SimpleNamespace(rule=SimpleNamespace(id=x)) for x in rules),
        effective_shooting=shoot, effective_defence=defence,
        profile=SimpleNamespace(keywords=()),
    )


def run(*, spend=LethalAimSpend.TO_HIT, index=0, free=True, shots=1,
        extra_rules=(), state=None, range_inches=12, in_way=()):
    return calculate_lethal_aim_volley_evidence(
        attacker=model(rules=('LETHAL_AIM', 'EXPERT_SHOT') + extra_rules),
        defender=model(),
        weapon=RangedWeaponProfile('WG_ORC_BOW',18,2,shots),
        defender_state=state or DefensiveState(1),
        context=ShootingContext(target_distance_inches=range_inches),
        clear_line_of_sight=True,
        lethal_aim_state=LethalAimState(free_might_available=free),
        lethal_aim_spend=spend, lethal_aim_shot_index=index,
        in_the_way_required_rolls=in_way,
    )


def test_expert_shot_allocates_bonus_to_one_shot_only():
    result = run()
    assert result.shots == 2
    assert result.shot_wound_probabilities[0] > result.shot_wound_probabilities[1]
    assert result.expected_wounds == sum(result.shot_wound_probabilities)


def test_second_shot_can_receive_bonus():
    a, b = run(index=0), run(index=1)
    assert a.shot_wound_probabilities == tuple(reversed(b.shot_wound_probabilities))
    assert a.incoming_wound_distribution == b.incoming_wound_distribution


def test_to_wound_bonus_only_affects_selected_shot():
    result = run(spend=LethalAimSpend.TO_WOUND)
    assert result.shot_wound_probabilities[0] > result.shot_wound_probabilities[1]


def test_in_the_way_bonus_only_affects_selected_shot():
    result = run(spend=LethalAimSpend.IN_THE_WAY,in_way=(4,))
    assert result.shot_wound_probabilities[0] > result.shot_wound_probabilities[1]


def test_three_plus_shots_only_one_receives_bonus():
    result = run(shots=2)
    assert result.shots == 4
    assert result.shot_wound_probabilities[1:] == (result.shot_wound_probabilities[1],) * 3


def test_fate_resolves_once_across_volley():
    no_fate = run(state=DefensiveState(1))
    fate = run(state=DefensiveState(1,remaining_fate=1))
    assert fate.elimination_probability < no_fate.elimination_probability
    assert sum(fate.incoming_wound_distribution) == 1


@pytest.mark.parametrize('index', [-1, 2, True])
def test_invalid_shot_index_rejected(index):
    with pytest.raises(ValueError,match='shot index'):
        run(index=index)


def test_unavailable_might_rejected():
    with pytest.raises(ValueError,match='invalid Lethal Aim'):
        run(free=False)


def test_out_of_range_rejected():
    with pytest.raises(ValueError,match='cannot fire'):
        run(range_inches=19)
