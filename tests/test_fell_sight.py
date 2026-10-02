from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from fell_sight import (
    ignores_charge_line_of_sight_requirement,
    ignores_stalk_unseen_restriction,
)
from mount import Mount
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule


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
    )


def test_fell_sight_removes_charge_line_of_sight_requirement():
    profile = make_profile(
        "FELL_WARG",
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="FELL_SIGHT",
                name="Fell Sight",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    configured = ConfiguredProfile(
        profile=profile,
    )

    assert (
        ignores_charge_line_of_sight_requirement(
            configured,
        )
        is True
    )


def test_model_without_fell_sight_still_requires_charge_line_of_sight():
    configured = ConfiguredProfile(
        profile=make_profile(
            "NORMAL_MODEL",
        ),
    )

    assert (
        ignores_charge_line_of_sight_requirement(
            configured,
        )
        is False
    )


def test_fell_sight_ignores_stalk_unseen():
    attacker_profile = make_profile(
        "ATTACKER",
    )

    attacker_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="FELL_SIGHT",
                name="Fell Sight",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    defender_profile = make_profile(
        "DEFENDER",
    )

    defender_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="STALK_UNSEEN",
                name="Stalk Unseen",
                category=RuleCategory.DEFENCE,
            ),
        )
    )

    attacker = ConfiguredProfile(
        profile=attacker_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    assert (
        ignores_stalk_unseen_restriction(
            attacker,
            defender,
        )
        is True
    )


def test_fell_warg_mount_grants_fell_sight_semantics_to_rider():
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

    defender_profile = make_profile(
        "DEFENDER",
    )

    defender_profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="STALK_UNSEEN",
                name="Stalk Unseen",
                category=RuleCategory.DEFENCE,
            ),
        )
    )

    rider = ConfiguredProfile(
        profile=rider_profile,
    )

    defender = ConfiguredProfile(
        profile=defender_profile,
    )

    assert (
        ignores_charge_line_of_sight_requirement(
            rider,
        )
        is True
    )

    assert (
        ignores_stalk_unseen_restriction(
            rider,
            defender,
        )
        is True
    )