from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from stand_fast_eligibility import (
    can_provide_stand_fast,
)


def make_profile() -> Profile:
    return Profile(
        id="TEST_HERO",
        name="Test Hero",
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="7+",
        might=1,
        will=1,
        fate=1,
        max_in_army=0,
    )


def test_normal_hero_can_provide_stand_fast():
    configured = ConfiguredProfile(
        profile=make_profile(),
    )

    assert can_provide_stand_fast(
        configured,
    ) is True


def test_automatons_cannot_provide_stand_fast():
    profile = make_profile()

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="AUTOMATONS",
                name="Automatons",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert can_provide_stand_fast(
        configured,
    ) is False