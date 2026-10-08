from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from shooting_attack_count import (
    get_effective_shooting_attack_count,
)


def make_shooter(*, expert_shot: bool) -> ConfiguredProfile:
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

    if expert_shot:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="EXPERT_SHOT",
                    name="Expert Shot",
                    category=RuleCategory.SHOOTING,
                ),
            )
        )

    return ConfiguredProfile(
        profile=profile,
    )


def test_normal_shooter_makes_one_shooting_attack():
    assert (
        get_effective_shooting_attack_count(
            make_shooter(expert_shot=False),
        )
        == 1
    )


def test_expert_shot_makes_two_shooting_attacks():
    assert (
        get_effective_shooting_attack_count(
            make_shooter(expert_shot=True),
        )
        == 2
    )

def test_deadly_shot_makes_three_shooting_attacks():
    profile = Profile(
        id="LEGOLAS_TEST",
        name="Legolas Test",
        points=0,
        movement=6,
        fight=6,
        shooting="3+",
        strength=4,
        defence=4,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="4+",
        might=3,
        will=2,
        fate=3,
        max_in_army=1,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="DEADLY_SHOT",
                name="Deadly Shot",
                category=RuleCategory.SHOOTING,
            ),
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert (
        get_effective_shooting_attack_count(
            configured,
        )
        == 3
    )