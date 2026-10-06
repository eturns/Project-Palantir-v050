from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from mount import Mount
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from terrain_movement import (
    get_effective_movement_in_terrain,
    ignores_difficult_terrain_movement_penalty,
)


def make_mounted_profile(
    *,
    hunt_master: bool = False,
) -> ConfiguredProfile:
    profile = Profile(
        id="TEST_RIDER",
        name="Test Rider",
        points=20,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="7+",
        might=2,
        will=1,
        fate=1,
        max_in_army=1,
    )

    profile.default_mount = Mount(
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
    )

    if hunt_master:
        profile.special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id="HUNT_MASTER",
                    name="Hunt Master",
                    category=RuleCategory.SPECIAL,
                ),
            )
        )

    return ConfiguredProfile(
        profile=profile,
    )


def test_normal_mounted_model_halves_movement_in_difficult_terrain():
    rider = make_mounted_profile()

    assert (
        get_effective_movement_in_terrain(
            rider,
            in_difficult_terrain=True,
        )
        == 5.0
    )


def test_hunt_master_ignores_difficult_terrain_movement_penalty():
    fimbul = make_mounted_profile(
        hunt_master=True,
    )

    assert (
        get_effective_movement_in_terrain(
            fimbul,
            in_difficult_terrain=True,
        )
        == 10.0
    )


def test_hunt_master_only_ignores_penalty_while_cavalry():
    profile = Profile(
        id="FIMBUL",
        name="Fimbul",
        points=50,
        movement=6,
        fight=4,
        shooting="5+",
        strength=4,
        defence=5,
        attacks=2,
        wounds=2,
        courage="6+",
        intelligence="7+",
        might=2,
        will=1,
        fate=1,
        max_in_army=1,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="HUNT_MASTER",
                name="Hunt Master",
                category=RuleCategory.SPECIAL,
            ),
        )
    )

    fimbul = ConfiguredProfile(
        profile=profile,
    )

    assert (
        ignores_difficult_terrain_movement_penalty(
            fimbul
        )
        is False
    )


def test_open_ground_movement_is_unchanged():
    fimbul = make_mounted_profile(
        hunt_master=True,
    )

    assert (
        get_effective_movement_in_terrain(
            fimbul,
            in_difficult_terrain=False,
        )
        == 10.0
    )