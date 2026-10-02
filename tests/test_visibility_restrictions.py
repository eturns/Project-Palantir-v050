from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_classification import ModelType
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from visibility_restrictions import (
    VisibilityContext,
    can_be_seen_by,
)


def make_profile(
    profile_id: str,
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
        courage="7+",
        intelligence="7+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        model_types={
            ModelType.INFANTRY,
        },
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


def test_stalk_unseen_blocks_visibility_beyond_six_inches():
    observer = ConfiguredProfile(
        profile=make_profile(
            "OBSERVER",
        ),
    )

    target_profile = make_profile(
        "TARGET",
    )

    add_rule(
        target_profile,
        "STALK_UNSEEN",
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=7,
            partially_concealed_by_terrain=True,
        ),
    ) is False


def test_stalk_unseen_does_not_block_within_six_inches():
    observer = ConfiguredProfile(
        profile=make_profile(
            "OBSERVER",
        ),
    )

    target_profile = make_profile(
        "TARGET",
    )

    add_rule(
        target_profile,
        "STALK_UNSEEN",
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=6,
            partially_concealed_by_terrain=True,
        ),
    ) is True


def test_clear_view_bypasses_stalk_unseen():
    observer = ConfiguredProfile(
        profile=make_profile(
            "OBSERVER",
        ),
    )

    target_profile = make_profile(
        "TARGET",
    )

    add_rule(
        target_profile,
        "STALK_UNSEEN",
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=12,
            partially_concealed_by_terrain=True,
            completely_clear_view=True,
        ),
    ) is True


def test_fell_sight_bypasses_stalk_unseen():
    observer_profile = make_profile(
        "OBSERVER",
    )

    add_rule(
        observer_profile,
        "FELL_SIGHT",
    )

    target_profile = make_profile(
        "TARGET",
    )

    add_rule(
        target_profile,
        "STALK_UNSEEN",
    )

    observer = ConfiguredProfile(
        profile=observer_profile,
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=12,
            partially_concealed_by_terrain=True,
        ),
    ) is True


def test_silent_hunters_blocks_visibility_in_woodland_beyond_six():
    observer = ConfiguredProfile(
        profile=make_profile(
            "OBSERVER",
        ),
    )

    target_profile = make_profile(
        "HUNTING_SPIDER",
    )

    add_rule(
        target_profile,
        "SILENT_HUNTERS",
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=7,
            in_woodland=True,
        ),
    ) is False


def test_silent_hunters_applies_when_partially_concealed_by_woodland():
    observer = ConfiguredProfile(
        profile=make_profile(
            "OBSERVER",
        ),
    )

    target_profile = make_profile(
        "HUNTING_SPIDER",
    )

    add_rule(
        target_profile,
        "SILENT_HUNTERS",
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=10,
            partially_concealed_by_woodland=True,
        ),
    ) is False


def test_fell_sight_does_not_bypass_silent_hunters():
    observer_profile = make_profile(
        "OBSERVER",
    )

    add_rule(
        observer_profile,
        "FELL_SIGHT",
    )

    target_profile = make_profile(
        "HUNTING_SPIDER",
    )

    add_rule(
        target_profile,
        "SILENT_HUNTERS",
    )

    observer = ConfiguredProfile(
        profile=observer_profile,
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    assert can_be_seen_by(
        observer,
        target,
        VisibilityContext(
            distance_inches=10,
            in_woodland=True,
        ),
    ) is False