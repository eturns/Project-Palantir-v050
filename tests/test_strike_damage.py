from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)


def test_strike_damage_defaults_to_one_wound():
    damage = StrikeDamage()

    assert damage.wounds_per_successful_strike == 1


def test_strike_damage_can_represent_multiple_wounds():
    damage = StrikeDamage(
        wounds_per_successful_strike=2,
    )

    assert damage.wounds_per_successful_strike == 2

def test_strike_damage_can_represent_d3_wounds():
    damage = StrikeDamage(
        damage_type=StrikeDamageType.D3,
    )

    assert damage.damage_type == StrikeDamageType.D3