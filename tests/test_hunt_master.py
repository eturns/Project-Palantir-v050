from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from hunt_master import (
    get_hunt_master_fight_bonus,
    hunt_master_allows_difficult_terrain_charge_bonus,
)
from mount import Mount
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from database.rule_category import RuleCategory


def make_fimbul():
    profile = Profile(
        id="FIMBUL",
        name="Fimbul, Hunter Orc Captain",
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


def test_hunt_master_gives_plus_one_fight_when_charging():
    fimbul = make_fimbul()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
    )

    assert (
        get_hunt_master_fight_bonus(
            fimbul,
            context,
        )
        == 1
    )


def test_hunt_master_gives_no_fight_bonus_when_charged():
    fimbul = make_fimbul()

    context = CombatContext(
        engagement_role=EngagementRole.WAS_CHARGED,
    )

    assert (
        get_hunt_master_fight_bonus(
            fimbul,
            context,
        )
        == 0
    )


def test_hunt_master_allows_charge_bonus_in_difficult_terrain():
    fimbul = make_fimbul()

    context = CombatContext(
        engagement_role=EngagementRole.CHARGED,
        in_difficult_terrain=True,
    )

    assert (
        hunt_master_allows_difficult_terrain_charge_bonus(
            fimbul,
            context,
        )
        is True
    )