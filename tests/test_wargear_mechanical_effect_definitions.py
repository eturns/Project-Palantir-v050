from configured_profile import ConfiguredProfile
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from melee_weapon_selection import MeleeWeaponSelection
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from roll_modifier_mechanical_effect import (
    RollModifierMechanicalEffect,
)
from database.rule_category import RuleCategory
from special_rule import SpecialRule
from wargear import Wargear
from wargear_mechanical_effect_definitions import (
    BURLY_RULE_ID,
    TWO_HANDED_WEAPON_ID,
    get_wargear_mechanical_effect_definitions,
)


def make_profile_with_two_handed_weapon(
    *,
    has_burly: bool = False,
) -> ConfiguredProfile:
    special_rules = []

    if has_burly:
        special_rules.append(
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id=BURLY_RULE_ID,
                    name="Burly",
                    category=RuleCategory.OFFENCE,
                ),
            )
        )

    profile = Profile(
        id="TEST",
        name="Test Model",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        default_wargear=[
            Wargear(
                id=TWO_HANDED_WEAPON_ID,
                name="Two-Handed Weapon",
            ),
        ],
        special_rules=special_rules,
    )

    return ConfiguredProfile(
        profile=profile,
    )


def test_two_handed_weapon_creates_wound_and_duel_modifiers():
    definitions = (
        get_wargear_mechanical_effect_definitions(
            make_profile_with_two_handed_weapon(),
        )
    )

    assert len(definitions) == 2

    wound_definition = definitions[0]
    wound_effect = wound_definition.effect

    assert isinstance(
        wound_effect,
        RollModifierMechanicalEffect,
    )
    assert wound_effect.effect_type is (
        MechanicalEffectType.ROLL_MODIFIER
    )
    assert wound_effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert wound_effect.source_id == TWO_HANDED_WEAPON_ID
    assert wound_effect.value == 1
    assert wound_effect.ignored_on_natural_six is False

    duel_definition = definitions[1]
    duel_effect = duel_definition.effect

    assert isinstance(
        duel_effect,
        RollModifierMechanicalEffect,
    )
    assert duel_effect.effect_type is (
        MechanicalEffectType.ROLL_MODIFIER
    )
    assert duel_effect.target is (
        MechanicalEffectTarget.DUEL_ROLL
    )
    assert duel_effect.source_id == TWO_HANDED_WEAPON_ID
    assert duel_effect.value == -1
    assert duel_effect.ignored_on_natural_six is True

    assert (
        wound_definition.applicability.applicability_type
        is MechanicalEffectApplicabilityType.ANY
    )
    assert (
        duel_definition.applicability.applicability_type
        is MechanicalEffectApplicabilityType.ANY
    )


def test_two_handed_weapon_with_burly_keeps_wound_bonus_only():
    definitions = (
        get_wargear_mechanical_effect_definitions(
            make_profile_with_two_handed_weapon(
                has_burly=True,
            ),
        )
    )

    assert len(definitions) == 1
    assert definitions[0].effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert definitions[0].effect.value == 1


def test_additional_burly_keeps_wound_bonus_only():
    definitions = (
        get_wargear_mechanical_effect_definitions(
            make_profile_with_two_handed_weapon(),
            additional_burly=True,
        )
    )

    assert len(definitions) == 1
    assert definitions[0].effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )


def test_two_handed_weapon_respects_selected_weapon():
    configured_profile = (
        make_profile_with_two_handed_weapon()
    )

    definitions = (
        get_wargear_mechanical_effect_definitions(
            configured_profile,
            selection=MeleeWeaponSelection(
                wargear_id="OTHER_WEAPON",
            ),
        )
    )

    assert definitions == ()