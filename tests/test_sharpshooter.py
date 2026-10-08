from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from sharpshooter import (
    requires_cavalry_part_in_the_way_test,
)
from special_rule import SpecialRule


def make_shooter(
    *,
    sharpshooter: bool,
) -> ConfiguredProfile:
    profile = Profile(
        id="TEST_SHOOTER",
        name="Test Shooter",
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

    if sharpshooter:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="SHARPSHOOTER",
                    name="Sharpshooter",
                    category=RuleCategory.SHOOTING,
                ),
            )
        )

    return ConfiguredProfile(
        profile=profile,
    )


def test_normal_shooter_requires_cavalry_part_in_the_way_test():
    assert (
        requires_cavalry_part_in_the_way_test(
            make_shooter(
                sharpshooter=False,
            ),
            target_is_cavalry=True,
        )
        is True
    )


def test_sharpshooter_skips_cavalry_part_in_the_way_test():
    assert (
        requires_cavalry_part_in_the_way_test(
            make_shooter(
                sharpshooter=True,
            ),
            target_is_cavalry=True,
        )
        is False
    )


def test_non_cavalry_target_never_requires_cavalry_part_test():
    assert (
        requires_cavalry_part_in_the_way_test(
            make_shooter(
                sharpshooter=False,
            ),
            target_is_cavalry=False,
        )
        is False
    )