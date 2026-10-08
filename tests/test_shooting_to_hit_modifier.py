from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from shooting_to_hit_modifier import (
    get_movement_shooting_modifier,
)


def make_profile(
    *,
    deadly_shot: bool,
    keywords: set[str] | None = None,
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

    profile.keywords = set(
        keywords or set()
    )

    if deadly_shot:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="DEADLY_SHOT",
                    name="Deadly Shot",
                    category=RuleCategory.SHOOTING,
                ),
            )
        )

    return ConfiguredProfile(
        profile=profile,
    )


def test_normal_infantry_gets_minus_one_after_moving():
    profile = make_profile(
        deadly_shot=False,
        keywords={"INFANTRY"},
    )

    assert (
        get_movement_shooting_modifier(
            profile,
            moved_this_turn=True,
        )
        == -1
    )


def test_deadly_shot_infantry_ignores_moving_penalty():
    profile = make_profile(
        deadly_shot=True,
        keywords={"INFANTRY"},
    )

    assert (
        get_movement_shooting_modifier(
            profile,
            moved_this_turn=True,
        )
        == 0
    )


def test_deadly_shot_without_infantry_still_gets_penalty():
    profile = make_profile(
        deadly_shot=True,
        keywords={"CAVALRY"},
    )

    assert (
        get_movement_shooting_modifier(
            profile,
            moved_this_turn=True,
        )
        == -1
    )


def test_stationary_shooter_gets_no_movement_penalty():
    profile = make_profile(
        deadly_shot=False,
        keywords={"INFANTRY"},
    )

    assert (
        get_movement_shooting_modifier(
            profile,
            moved_this_turn=False,
        )
        == 0
    )