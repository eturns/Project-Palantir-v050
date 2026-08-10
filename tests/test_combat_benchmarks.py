from fractions import Fraction
import pytest
from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from wargear import Wargear


def create_benchmark_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_benchmark_equal_fight_equal_attacks():
    attacker = ConfiguredProfile(
        profile=create_benchmark_profile(
            "ATTACKER",
        )
    )

    defender = ConfiguredProfile(
        profile=create_benchmark_profile(
            "DEFENDER",
        )
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
    )

    assert (
        result.attacker_win_probability
        == Fraction(1, 2)
    )


def test_benchmark_two_handed_weapon_duel_penalty():
    attacker_profile = create_benchmark_profile(
        "ATTACKER",
    )

    attacker_profile.default_wargear.append(
        Wargear(
            id="WG_TWO_HANDED_WEAPON",
            name="Two-handed Weapon",
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=create_benchmark_profile(
            "DEFENDER",
        )
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
    )

    assert result.attacker_win_probability == pytest.approx(
    7 / 18
)


def test_benchmark_burly_cancels_two_handed_duel_penalty():
    attacker_profile = create_benchmark_profile(
        "ATTACKER",
    )

    attacker_profile.default_wargear.append(
        Wargear(
            id="WG_TWO_HANDED_WEAPON",
            name="Two-handed Weapon",
        )
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="BURLY",
                name="Burly",
                category=RuleCategory.SPECIAL,
            ),
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=create_benchmark_profile(
            "DEFENDER",
        )
    )

    result = calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
    )

    assert (
        result.attacker_win_probability
        == Fraction(1, 2)
    )