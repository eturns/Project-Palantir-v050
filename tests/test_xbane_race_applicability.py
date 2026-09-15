from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from fielded_model import FieldedModel
from mechanical_effect_definition_matcher import (
    mechanical_effect_definition_applies_to_fielded_model,
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
from fielded_strike_damage_resolver import (
    resolve_strike_damage_for_models,
)
from strike_damage import StrikeDamageType
from fractions import Fraction

from defensive_state import DefensiveState
from survival_probability import (
    get_survival_probability_after_strike_damage,
)

def make_xbane_attacker() -> ConfiguredProfile:
    profile = Profile(
        id="ATTACKER",
        name="Attacker",
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
                parameter="ORC",
            ),
        ],
    )

    return ConfiguredProfile(
        profile=profile,
    )


def make_defender(
    *,
    races: list[str],
    keywords: list[str],
) -> FieldedModel:
    profile = Profile(
        id="DEFENDER",
        name="Defender",
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
        races=races,
        keywords=keywords,
    )

    return FieldedModel(
        id="DEFENDER-1",
        configured_profile=ConfiguredProfile(
            profile=profile,
        ),
    )


def test_xbane_applies_when_race_matches_without_keyword():
    definition = (
        get_special_rule_mechanical_effect_definitions(
            make_xbane_attacker(),
        )[0]
    )

    defender = make_defender(
        races=["ORC"],
        keywords=[],
    )

    assert (
        mechanical_effect_definition_applies_to_fielded_model(
            definition,
            defender,
        )
        is True
    )


def test_xbane_does_not_apply_to_keyword_only_match():
    definition = (
        get_special_rule_mechanical_effect_definitions(
            make_xbane_attacker(),
        )[0]
    )

    defender = make_defender(
        races=["MAN"],
        keywords=["ORC"],
    )

    assert (
        mechanical_effect_definition_applies_to_fielded_model(
            definition,
            defender,
        )
        is False
    )

def test_fielded_strike_damage_resolver_returns_xbane_damage():
    attacker = FieldedModel(
        id="ATTACKER-1",
        configured_profile=make_xbane_attacker(),
    )

    defender = make_defender(
        races=["ORC"],
        keywords=[],
    )

    result = resolve_strike_damage_for_models(
        attacker,
        defender,
    )

    assert len(result) == 1
    assert result[0].damage_type is StrikeDamageType.D3

def test_fielded_strike_damage_resolver_ignores_keyword_only_xbane_match():
    attacker = FieldedModel(
        id="ATTACKER-1",
        configured_profile=make_xbane_attacker(),
    )

    defender = make_defender(
        races=["MAN"],
        keywords=["ORC"],
    )

    result = resolve_strike_damage_for_models(
        attacker,
        defender,
    )

    assert result == ()

def test_fielded_strike_damage_resolver_ignores_wrong_race():
    attacker = FieldedModel(
        id="ATTACKER-1",
        configured_profile=make_xbane_attacker(),
    )

    defender = make_defender(
        races=["MAN"],
        keywords=[],
    )

    result = resolve_strike_damage_for_models(
        attacker,
        defender,
    )

    assert result == ()

def test_xbane_d3_reaches_survival_probability():
    attacker = FieldedModel(
        id="ATTACKER-1",
        configured_profile=make_xbane_attacker(),
    )

    defender = make_defender(
        races=["ORC"],
        keywords=[],
    )

    damage = resolve_strike_damage_for_models(
        attacker,
        defender,
    )[0]

    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=0,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage,
    )

    assert result == Fraction(1, 3)

def test_xbane_d3_preserves_single_strike_fate_semantics():
    attacker = FieldedModel(
        id="ATTACKER-1",
        configured_profile=make_xbane_attacker(),
    )

    defender = make_defender(
        races=["ORC"],
        keywords=[],
    )

    damage = resolve_strike_damage_for_models(
        attacker,
        defender,
    )[0]

    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage,
    )

    assert result == Fraction(2, 3)