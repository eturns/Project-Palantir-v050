from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from charge_visibility import (
    ChargeVisibilityContext,
    can_charge_based_on_visibility,
)
from mount import Mount
from profile_classification import ModelType
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from visibility_restrictions import (
    VisibilityContext,
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


def test_normal_model_requires_line_of_sight_to_charge():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
        ),
    )

    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = can_charge_based_on_visibility(
        attacker,
        target,
        ChargeVisibilityContext(
            has_line_of_sight=False,
            visibility=VisibilityContext(
                distance_inches=4,
            ),
        ),
    )

    assert result is False


def test_normal_model_can_charge_visible_target():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
        ),
    )

    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = can_charge_based_on_visibility(
        attacker,
        target,
        ChargeVisibilityContext(
            has_line_of_sight=True,
            visibility=VisibilityContext(
                distance_inches=4,
            ),
        ),
    )

    assert result is True


def test_stalk_unseen_can_prevent_charge_beyond_six_inches():
    attacker = ConfiguredProfile(
        profile=make_profile(
            "ATTACKER",
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

    result = can_charge_based_on_visibility(
        attacker,
        target,
        ChargeVisibilityContext(
            has_line_of_sight=True,
            visibility=VisibilityContext(
                distance_inches=8,
                partially_concealed_by_terrain=True,
            ),
        ),
    )

    assert result is False


def test_fell_sight_can_charge_without_line_of_sight():
    attacker_profile = make_profile(
        "FELL_WARG",
    )

    add_rule(
        attacker_profile,
        "FELL_SIGHT",
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = can_charge_based_on_visibility(
        attacker,
        target,
        ChargeVisibilityContext(
            has_line_of_sight=False,
            visibility=VisibilityContext(
                distance_inches=8,
            ),
        ),
    )

    assert result is True


def test_fell_sight_can_charge_stalk_unseen_target():
    attacker_profile = make_profile(
        "FELL_WARG",
    )

    add_rule(
        attacker_profile,
        "FELL_SIGHT",
    )

    target_profile = make_profile(
        "TARGET",
    )

    add_rule(
        target_profile,
        "STALK_UNSEEN",
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    target = ConfiguredProfile(
        profile=target_profile,
    )

    result = can_charge_based_on_visibility(
        attacker,
        target,
        ChargeVisibilityContext(
            has_line_of_sight=False,
            visibility=VisibilityContext(
                distance_inches=10,
                partially_concealed_by_terrain=True,
            ),
        ),
    )

    assert result is True


def test_fell_warg_mount_grants_charge_visibility_benefit():
    rider_profile = make_profile(
        "RIDER",
    )

    rider_profile.default_mount = Mount(
        id="MOUNT_FELL_WARG",
        name="Fell Warg",
        movement=10,
        fight=3,
        shooting="6+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="8+",
        intelligence="7+",
        base_size_mm=40,
        special_rule_ids=frozenset(
            {
                "FELL_SIGHT",
            }
        ),
    )

    attacker = ConfiguredProfile(
        profile=rider_profile,
    )

    target = ConfiguredProfile(
        profile=make_profile(
            "TARGET",
        ),
    )

    result = can_charge_based_on_visibility(
        attacker,
        target,
        ChargeVisibilityContext(
            has_line_of_sight=False,
            visibility=VisibilityContext(
                distance_inches=8,
            ),
        ),
    )

    assert result is True