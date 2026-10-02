from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from runtime_special_rules import (
    get_effective_runtime_rule_ids,
)
from special_rule import SpecialRule
from torturer_state import TorturerState


def make_profile() -> Profile:
    return Profile(
        id="KEEPER_TEST",
        name="Keeper Test",
        points=80,
        movement=6,
        fight=5,
        shooting="5+",
        strength=5,
        defence=6,
        attacks=3,
        wounds=2,
        courage="5+",
        intelligence="6+",
        might=3,
        will=3,
        fate=0,
        max_in_army=1,
    )


def add_torturer(profile: Profile) -> None:
    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="TORTURER",
                name="Torturer",
                category=RuleCategory.SPECIAL,
            ),
        )
    )


def test_runtime_rules_include_static_rules():
    profile = make_profile()
    add_torturer(profile)

    configured = ConfiguredProfile(
        profile=profile,
    )

    result = get_effective_runtime_rule_ids(
        configured,
    )

    assert "TORTURER" in result
    assert "TERROR" not in result


def test_runtime_rules_add_terror_at_three_kills():
    profile = make_profile()
    add_torturer(profile)

    configured = ConfiguredProfile(
        profile=profile,
    )

    result = get_effective_runtime_rule_ids(
        configured,
        torturer_state=TorturerState(
            kills_in_combat=3,
        ),
    )

    assert "TORTURER" in result
    assert "TERROR" in result


def test_non_torturer_does_not_gain_terror_from_torturer_state():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    result = get_effective_runtime_rule_ids(
        configured,
        torturer_state=TorturerState(
            kills_in_combat=5,
        ),
    )

    assert "TERROR" not in result