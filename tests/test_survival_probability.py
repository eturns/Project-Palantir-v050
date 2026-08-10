from fractions import Fraction

import pytest

from defensive_state import DefensiveState
from survival_probability import (
    get_survival_probability_after_one_wound,
    get_survival_probability_after_wounds,
)
from strike_damage import StrikeDamage

from survival_probability import (
    get_configured_survival_probability_after_strike_damage,
    get_survival_probability_after_one_wound,
    get_survival_probability_after_strike_damage,
    get_survival_probability_after_wounds,
)
from configured_profile import ConfiguredProfile
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from special_rule import SpecialRule
from database.rule_category import RuleCategory
from test_profiles import create_test_profile

def test_already_slain_model_has_zero_survival_probability():
    state = DefensiveState(
        remaining_wounds=0,
        remaining_fate=2,
    )

    result = get_survival_probability_after_one_wound(
        state,
    )

    assert result == Fraction(0, 1)


def test_multi_wound_model_survives_one_wound_without_fate():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=0,
    )

    result = get_survival_probability_after_one_wound(
        state,
    )

    assert result == Fraction(1, 1)


def test_last_wound_model_without_fate_is_slain():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
    )

    result = get_survival_probability_after_one_wound(
        state,
    )

    assert result == Fraction(0, 1)


def test_last_wound_model_with_one_fate_has_half_survival_probability():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=1,
    )

    result = get_survival_probability_after_one_wound(
        state,
    )

    assert result == Fraction(1, 2)


def test_last_wound_model_can_use_might_on_fate():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=1,
    )

    result = get_survival_probability_after_one_wound(
        state,
        might_points=1,
    )

    assert result == Fraction(2, 3)


def test_survival_probability_rejects_negative_might():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=1,
    )

    with pytest.raises(
        ValueError,
        match="Might points cannot be negative.",
    ):
        get_survival_probability_after_one_wound(
            state,
            might_points=-1,
        )

def test_zero_incoming_wounds_are_always_survived():
    state = DefensiveState(
        remaining_wounds=1,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=0,
    )

    assert result == Fraction(1, 1)


def test_two_wound_model_dies_from_two_unprevented_wounds():
    state = DefensiveState(
        remaining_wounds=2,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=2,
    )

    assert result == Fraction(0, 1)


def test_two_wound_model_with_one_fate_survives_two_wounds_half_the_time():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=2,
    )

    assert result == Fraction(1, 2)


def test_two_wound_model_with_two_fate_survives_two_wounds_three_quarters():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=2,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=2,
    )

    assert result == Fraction(3, 4)


def test_one_wound_model_must_prevent_both_of_two_incoming_wounds():
    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=2,
    )

    result = get_survival_probability_after_wounds(
        state,
        incoming_wounds=2,
    )

    assert result == Fraction(1, 4)


def test_might_is_depleted_across_multiple_incoming_wounds():
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


def test_multiple_wound_survival_rejects_negative_incoming_wounds():
    state = DefensiveState(
        remaining_wounds=2,
    )

    with pytest.raises(
        ValueError,
        match="Incoming wounds cannot be negative.",
    ):
        get_survival_probability_after_wounds(
            state,
            incoming_wounds=-1,
        )

def test_model_survives_non_lethal_fixed_strike_damage():
    state = DefensiveState(
        remaining_wounds=2,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage=StrikeDamage(),
    )

    assert result == Fraction(1, 1)


def test_mighty_blow_can_slay_two_wound_model():
    state = DefensiveState(
        remaining_wounds=2,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage=StrikeDamage(
            wounds_per_successful_strike=2,
        ),
    )

    assert result == Fraction(0, 1)


def test_one_fate_can_prevent_all_mighty_blow_damage():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage=StrikeDamage(
            wounds_per_successful_strike=2,
        ),
    )

    assert result == Fraction(1, 2)


def test_might_can_improve_fate_against_mighty_blow():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
    )

    result = get_survival_probability_after_strike_damage(
        state,
        damage=StrikeDamage(
            wounds_per_successful_strike=2,
        ),
        might_points=1,
    )

    assert result == Fraction(2, 3)

def test_normal_model_cannot_use_will_to_survive_strike():
    profile = create_test_profile(
        profile_id="TEST_NORMAL_DEFENDER",
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=3,
    )

    result = (
        get_configured_survival_probability_after_strike_damage(
            defender,
            state,
            damage=StrikeDamage(),
        )
    )

    assert result == Fraction(0, 1)

def test_will_as_fate_can_prevent_lethal_strike():
    profile = create_test_profile(
        profile_id="TEST_NECROMANCER",
    )

    will_as_fate = SpecialRule(
        id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        name="He Cannot Yet Take Physical Form",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=will_as_fate,
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

def test_will_as_fate_can_use_multiple_will_attempts():
    profile = create_test_profile(
        profile_id="TEST_NECROMANCER",
    )

    will_as_fate = SpecialRule(
        id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        name="He Cannot Yet Take Physical Form",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=will_as_fate,
            parameter=None,
        )
    )

    defender = ConfiguredProfile(
        profile=profile,
    )

    state = DefensiveState(
        remaining_wounds=1,
        remaining_fate=0,
        remaining_will=2,
    )

    result = (
        get_configured_survival_probability_after_strike_damage(
            defender,
            state,
            damage=StrikeDamage(),
        )
    )

    assert result == Fraction(3, 4)

def test_might_can_improve_will_used_as_fate():
    profile = create_test_profile(
        profile_id="TEST_NECROMANCER",
    )

    will_as_fate = SpecialRule(
        id="HE_CANNOT_YET_TAKE_PHYSICAL_FORM",
        name="He Cannot Yet Take Physical Form",
        category=RuleCategory.SPECIAL,
    )

    profile.special_rules.append(
        ProfileSpecialRuleAssignment(
            rule=will_as_fate,
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
            might_points=1,
        )
    )

    assert result == Fraction(2, 3)