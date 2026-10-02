from fractions import Fraction

from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from terror_charge import (
    calculate_terror_charge_success_probability,
)
from torturer_state import TorturerState


def make_profile(
    profile_id: str,
    courage: str = "7+",
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
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


def test_charge_against_non_terror_model_is_automatic():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
        ),
    )

    defender = ConfiguredProfile(
        profile=make_profile(
            "DEFENDER",
        ),
    )

    assert (
        calculate_terror_charge_success_probability(
            attacker,
            defender,
        )
        == Fraction(1, 1)
    )


def test_charge_against_terror_uses_attacker_courage():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
            courage="7+",
        ),
    )

    defender_profile = make_profile(
        "DEFENDER",
    )

    add_rule(
        defender_profile,
        "TERROR",
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    assert (
        calculate_terror_charge_success_probability(
            attacker,
            defender,
        )
        == Fraction(21, 36)
    )


def test_automatic_courage_pass_ignores_terror_failure_chance():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
        ),
    )

    defender_profile = make_profile(
        "DEFENDER",
    )

    add_rule(
        defender_profile,
        "TERROR",
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    assert (
        calculate_terror_charge_success_probability(
            attacker,
            defender,
            attacker_courage_context=CourageTestContext(
                automatically_passes=True,
            ),
        )
        == Fraction(1, 1)
    )


def test_keeper_runtime_terror_applies_at_three_kills():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
            courage="7+",
        ),
    )

    keeper_profile = make_profile(
        "KEEPER",
    )

    add_rule(
        keeper_profile,
        "TORTURER",
    )

    keeper = ConfiguredProfile(
        profile=keeper_profile,
    )

    assert (
        calculate_terror_charge_success_probability(
            attacker,
            keeper,
            defender_torturer_state=TorturerState(
                kills_in_combat=3,
            ),
        )
        == Fraction(21, 36)
    )


def test_keeper_has_no_runtime_terror_before_three_kills():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
            courage="7+",
        ),
    )

    keeper_profile = make_profile(
        "KEEPER",
    )

    add_rule(
        keeper_profile,
        "TORTURER",
    )

    keeper = ConfiguredProfile(
        profile=keeper_profile,
    )

    assert (
        calculate_terror_charge_success_probability(
            attacker,
            keeper,
            defender_torturer_state=TorturerState(
                kills_in_combat=2,
            ),
        )
        == Fraction(1, 1)
    )