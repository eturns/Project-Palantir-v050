from fractions import Fraction

from loader import load_all_profiles
from wound_probability import get_profile_wound_probability
from wound_table import get_wound_target
from wound_target import WoundTarget


def test_real_profile_strength_and_defence_produce_wound_target():
    profiles = load_all_profiles()

    warrior = next(
        profile
        for profile in profiles
        if profile.id == "IH_WR"
    )

    assert get_wound_target(
        strength=warrior.strength,
        defence=warrior.defence,
    ) == WoundTarget(5)


def test_real_profile_wound_probability():
    profiles = load_all_profiles()

    warrior = next(
        profile
        for profile in profiles
        if profile.id == "IH_WR"
    )

    assert get_profile_wound_probability(
        attacker=warrior,
        defender=warrior,
    ) == Fraction(1, 3)