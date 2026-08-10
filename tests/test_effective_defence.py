from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule

from effective_defence import get_effective_defence


def create_test_profile(
    courage: str = "6+",
    defence: int = 4,
) -> Profile:
    return Profile(
        id="TEST",
        name="Test Profile",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=defence,
        attacks=1,
        wounds=1,
        courage=courage,
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_effective_defence_uses_normal_defence_without_blades_of_the_dead():
    attacker = ConfiguredProfile(
        profile=create_test_profile(),
    )

    defender = ConfiguredProfile(
        profile=create_test_profile(
            courage="8+",
            defence=6,
        ),
    )

    assert get_effective_defence(
        attacker,
        defender,
    ) == 6


def test_blades_of_the_dead_uses_ten_minus_courage():
    attacker_profile = create_test_profile()

    blades_of_the_dead = SpecialRule(
        id="BLADES_OF_THE_DEAD",
        name="Blades of the Dead",
        category=RuleCategory.SPECIAL,
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=blades_of_the_dead,
            parameter=None,
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=create_test_profile(
            courage="8+",
            defence=6,
        ),
    )

    assert get_effective_defence(
        attacker,
        defender,
    ) == 2