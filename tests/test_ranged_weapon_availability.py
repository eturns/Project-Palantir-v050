from ability_availability import ability_is_available
from ability_prerequisite_entity import AbilityPrerequisiteEntity
from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_option import ProfileOption
from profile_option_wargear_assignment import (
    ProfileOptionWargearAssignment,
    WargearAssignmentAction,
)
from profiles import Profile
from special_rule import SpecialRule
from wargear import Wargear

def test_ranged_weapon_prerequisite_uses_configured_wargear():
    warrior = Profile(
        id="TEST_WARRIOR",
        name="Test Warrior",
        points=10,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    crossbow = Wargear(
        id="WG_CROSSBOW",
        name="Crossbow",
    )

    crossbow_option = ProfileOption(
        id="TEST_CROSSBOW",
        name="Crossbow",
        points=2,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=crossbow,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )
    warrior.profile_options.append(crossbow_option)

    ranged_ability = SpecialRule(
        id="TEST_RANGED_ABILITY",
        name="Test Ranged Ability",
        category=RuleCategory.SHOOTING,
        prerequisites=[
            AbilityPrerequisiteEntity(
                id="HAS_RANGED_WEAPON",
                name="Has Ranged Weapon",
            ),
        ],
    )

    without_crossbow = ConfiguredProfile(
        profile=warrior,
    )
    with_crossbow = ConfiguredProfile(
        profile=warrior,
        selected_options=(crossbow_option,),
    )

    assert not ability_is_available(
        without_crossbow,
        ranged_ability,
    )
    assert ability_is_available(
        with_crossbow,
        ranged_ability,
    )

from ability_tag_assignment import AbilityTagAssignment
from ability_tag_entity import AbilityTagEntity
from battlefield_profile_evidence_builder import (
    build_profile_battlefield_evidence,
)


def test_purchased_crossbow_unlocks_shooting_evidence():
    warrior = Profile(
        id="TEST_WARRIOR",
        name="Test Warrior",
        points=10,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    crossbow = Wargear(id="WG_CROSSBOW", name="Crossbow")
    option = ProfileOption(
        id="TEST_CROSSBOW",
        name="Crossbow",
        points=2,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=crossbow,
                action=WargearAssignmentAction.GRANT,
            ),
        ),
    )
    warrior.profile_options.append(option)

    ranged_ability = SpecialRule(
        id="TEST_RANGED_ABILITY",
        name="Test Ranged Ability",
        category=RuleCategory.SHOOTING,
        ability_tags=[
            AbilityTagAssignment(
                tag=AbilityTagEntity(
                    id="SHOOTING",
                    name="Shooting",
                ),
                weight=1.0,
            ),
        ],
        prerequisites=[
            AbilityPrerequisiteEntity(
                id="HAS_RANGED_WEAPON",
                name="Has Ranged Weapon",
            ),
        ],
    )

    from profile_special_rule_assignment import (
        ProfileSpecialRuleAssignment,
    )

    warrior.special_rules.append(
        ProfileSpecialRuleAssignment(rule=ranged_ability)
    )

    without_crossbow = ConfiguredProfile(profile=warrior)
    with_crossbow = ConfiguredProfile(
        profile=warrior,
        selected_options=(option,),
    )

    assert not build_profile_battlefield_evidence(
        without_crossbow
    ).available_special_rules

    assert len(
        build_profile_battlefield_evidence(
            with_crossbow
        ).available_special_rules
    ) == 1