from fractions import Fraction

from configured_profile import ConfiguredProfile
from courage_test import (
    CourageTestContext,
    calculate_courage_test_success_probability,
)
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule


def make_profile(
    courage: str = "7+",
) -> Profile:
    return Profile(
        id="TEST",
        name="Test",
        points=10,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage=courage,
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def add_rule(
    profile: Profile,
    rule_id: str,
) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id=rule_id,
                name=rule_id,
                category=RuleCategory.SPECIAL,
            ),
        )
    )


def test_courage_seven_passes_twenty_one_of_thirty_six():
    configured = ConfiguredProfile(
        profile=make_profile(
            courage="7+",
        ),
    )

    assert (
        calculate_courage_test_success_probability(
            configured,
        )
        == Fraction(21, 36)
    )


def test_courage_four_passes_thirty_three_of_thirty_six():
    configured = ConfiguredProfile(
        profile=make_profile(
            courage="4+",
        ),
    )

    assert (
        calculate_courage_test_success_probability(
            configured,
        )
        == Fraction(33, 36)
    )


def test_context_can_force_automatic_pass():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    assert (
        calculate_courage_test_success_probability(
            configured,
            CourageTestContext(
                automatically_passes=True,
            ),
        )
        == Fraction(1, 1)
    )


def test_fearless_automatically_passes_courage_tests():
    profile = make_profile()

    add_rule(
        profile,
        "FEARLESS",
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert (
        calculate_courage_test_success_probability(
            configured,
        )
        == Fraction(1, 1)
    )