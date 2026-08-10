from fractions import Fraction

from configured_profile import ConfiguredProfile
from defensive_state import DefensiveState
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from strike_damage import StrikeDamage
from survival_probability import (
    get_configured_survival_probability_after_strike_damage,
    get_survival_probability_after_strike_damage,
    get_survival_probability_after_wounds,
)
from database.rule_category import RuleCategory
from test_profiles import create_test_profile

def test_two_separate_wounds_require_two_successful_preventions():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=2,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=2,
    )

    assert result == Fraction(1, 4)

def test_one_mighty_blow_strike_only_requires_one_successful_fate():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=1,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage=StrikeDamage(
            wounds_per_successful_strike=2,
        ),
    )

    assert result == Fraction(1, 2)

def test_might_is_not_spent_when_fate_succeeds_naturally():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=2,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=2,
        might_points=1,
    )

    assert result == Fraction(5, 12)

def test_will_is_not_available_as_fate_without_the_special_rule():
    profile = create_test_profile(
        profile_id="REGRESSION_NORMAL_MODEL",
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=25,
    )

    result = (
        get_configured_survival_probability_after_strike_damage(
            defender,
            state,
            damage=StrikeDamage(),
        )
    )

    assert result == Fraction(0, 1)

def test_necromancer_rule_makes_will_available_as_fate():
    profile = create_test_profile(
        profile_id="REGRESSION_NECROMANCER",
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
                name="He Cannot Yet Take Physical Form",
                category=RuleCategory.SPECIAL,
            ),
            parameter=None,
        )
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=1,
    )

    result = (
        get_configured_survival_probability_after_strike_damage(
            defender,
            state,
            damage=StrikeDamage(),
        )
    )

    assert result == Fraction(1, 2)

def test_necromancer_will_can_prevent_entire_mighty_blow_strike():
    profile = create_test_profile(
        profile_id="REGRESSION_NECROMANCER_MIGHTY_BLOW",
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=SpecialRule(
                id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
                name="He Cannot Yet Take Physical Form",
                category=RuleCategory.SPECIAL,
            ),
            parameter=None,
        )
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=1,
    )

    result = (
        get_configured_survival_probability_after_strike_damage(
            defender,
            state,
            damage=StrikeDamage(
                wounds_per_successful_strike=2,
            ),
        )
    )

    assert result == Fraction(1, 2)