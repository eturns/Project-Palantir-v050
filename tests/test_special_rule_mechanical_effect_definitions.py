from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope
from special_rule import SpecialRule
from special_rule_mechanical_effect_definitions import (
    BANE_OF_KINGS_RULE_ID,
    POISONED_ATTACKS_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)


def make_configured_profile(
    rule_ids: tuple[str, ...],
) -> ConfiguredProfile:
    special_rules = [
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id=rule_id,
                name=rule_id,
                category=RuleCategory.OFFENCE,
            ),
        )
        for rule_id in rule_ids
    ]

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
        special_rules=special_rules,
    )

    return ConfiguredProfile(
        profile=profile,
    )


def test_bane_of_kings_creates_failed_wound_reroll():
    definitions = (
        get_special_rule_mechanical_effect_definitions(
            make_configured_profile(
                (BANE_OF_KINGS_RULE_ID,),
            )
        )
    )

    assert len(definitions) == 1

    definition = definitions[0]
    effect = definition.effect

    assert isinstance(
        effect,
        RerollMechanicalEffect,
    )
    assert effect.effect_type is (
        MechanicalEffectType.REROLL
    )
    assert effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert effect.source_id == BANE_OF_KINGS_RULE_ID
    assert effect.scope is RerollScope.FAILED

    assert (
        definition.applicability.applicability_type
        is MechanicalEffectApplicabilityType.ANY
    )


def test_poisoned_attacks_creates_natural_one_reroll():
    definitions = (
        get_special_rule_mechanical_effect_definitions(
            make_configured_profile(
                (POISONED_ATTACKS_RULE_ID,),
            )
        )
    )

    assert len(definitions) == 1

    effect = definitions[0].effect

    assert isinstance(
        effect,
        RerollMechanicalEffect,
    )
    assert effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert effect.source_id == POISONED_ATTACKS_RULE_ID
    assert effect.scope is (
        RerollScope.NATURAL_ONES
    )


def test_multiple_special_rules_create_multiple_effects():
    definitions = (
        get_special_rule_mechanical_effect_definitions(
            make_configured_profile(
                (
                    BANE_OF_KINGS_RULE_ID,
                    POISONED_ATTACKS_RULE_ID,
                ),
            )
        )
    )

    assert tuple(
        definition.effect.scope
        for definition in definitions
    ) == (
        RerollScope.FAILED,
        RerollScope.NATURAL_ONES,
    )


def test_unrelated_special_rule_creates_no_effect():
    definitions = (
        get_special_rule_mechanical_effect_definitions(
            make_configured_profile(
                ("UNRELATED_RULE",),
            )
        )
    )

    assert definitions == ()