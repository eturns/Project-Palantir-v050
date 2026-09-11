from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profiles import Profile
from special_rule import SpecialRule
from special_rule_mechanical_effect_definitions import (
    XBANE_RULE_ID,
    get_special_rule_mechanical_effect_definitions,
)
from strike_damage import StrikeDamageType
from strike_damage_mechanical_effect import (
    StrikeDamageMechanicalEffect,
)


def make_xbane_profile(
    parameter: str | None,
) -> ConfiguredProfile:
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
        special_rules=[
            ProfileSpecialRuleAssignment(
                rule=SpecialRule(
                    id=XBANE_RULE_ID,
                    name="X-Bane",
                    category=RuleCategory.OFFENCE,
                ),
                parameter=parameter,
            ),
        ],
    )

    return ConfiguredProfile(
        profile=profile,
    )


def test_xbane_creates_d3_strike_damage_against_race():
    definitions = (
        get_special_rule_mechanical_effect_definitions(
            make_xbane_profile("orc"),
        )
    )

    assert len(definitions) == 1

    definition = definitions[0]
    effect = definition.effect

    assert isinstance(
        effect,
        StrikeDamageMechanicalEffect,
    )
    assert (
        effect.strike_damage.damage_type
        is StrikeDamageType.D3
    )

    assert (
        definition.applicability.applicability_type
        is MechanicalEffectApplicabilityType.RACE
    )
    assert definition.applicability.value == "ORC"


def test_xbane_without_parameter_creates_no_effect():
    definitions = (
        get_special_rule_mechanical_effect_definitions(
            make_xbane_profile(None),
        )
    )

    assert definitions == ()