"""DEV-077S-I2-E-B5-A RED — generic army Courage aggregation.

No assumed battlefield positions, Stand Fast availability or enemy profiles.
Probability and retention are measured for one specified test opportunity.
"""
from fractions import Fraction

import pytest

from army import Army
from configured_profile import ConfiguredProfile
from profiles import Profile
from database.rule_category import RuleCategory
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from special_rule import SpecialRule

from army_courage_aggregation import aggregate_army_courage


def make_profile(identifier, *, courage="7+", points=10, fearless=False):
    profile = Profile(
        id=identifier, name=identifier, points=points, movement=6,
        fight=3, shooting="4+", strength=3, defence=4,
        attacks=1, wounds=1, courage=courage, intelligence="7+",
        might=0, will=0, fate=0, max_in_army=0,
    )
    if fearless:
        profile.special_rules.append(ProfileSpecialRuleAssignment(
            rule=SpecialRule(id="FEARLESS", name="Fearless",
                             category=RuleCategory.SPECIAL)
        ))
    return ConfiguredProfile(profile=profile)


def make_army(*entries):
    army = Army()
    for configured, count in entries:
        army.add_configured_profile(configured, quantity=count)
    return army


def test_empty_army_has_zero_evidence_without_division_error():
    result = aggregate_army_courage(Army())
    assert result.model_count == 0
    assert result.army_points == 0
    assert result.average_test_pass_probability == Fraction(0, 1)
    assert result.expected_passes_per_test_window == Fraction(0, 1)
    assert result.passes_per_100_points == 0.0


def test_quantity_weighted_average_and_expected_passes():
    army = make_army(
        (make_profile("WEAK", courage="7+"), 3),
        (make_profile("STRONG", courage="4+"), 1),
    )
    result = aggregate_army_courage(army)
    assert result.model_count == 4
    assert result.average_test_pass_probability == Fraction(3 * 21 + 33, 4 * 36)
    assert result.expected_passes_per_test_window == Fraction(3 * 21 + 33, 36)


def test_fearless_contributes_full_probability_not_arbitrary_bonus():
    army = make_army(
        (make_profile("NORMAL"), 1),
        (make_profile("FEARLESS", fearless=True), 1),
    )
    result = aggregate_army_courage(army)
    assert result.average_test_pass_probability == (Fraction(21, 36) + 1) / 2
    assert result.expected_passes_per_test_window == Fraction(21, 36) + 1


def test_density_uses_total_army_points_including_purchases():
    army = make_army((make_profile("NORMAL", points=20), 2))
    army.add_purchase_points(10)
    result = aggregate_army_courage(army)
    assert result.army_points == 50
    assert result.passes_per_100_points == pytest.approx(
        float(Fraction(42, 36)) * 100 / 50
    )


def test_identical_profiles_have_same_average_despite_army_size():
    one = aggregate_army_courage(make_army((make_profile("ONE"), 1)))
    five = aggregate_army_courage(make_army((make_profile("FIVE"), 5)))
    assert one.average_test_pass_probability == five.average_test_pass_probability
    assert five.expected_passes_per_test_window == 5 * one.expected_passes_per_test_window


def test_baseline_does_not_assume_stand_fast_or_position():
    army = make_army((make_profile("NORMAL"), 1))
    result = aggregate_army_courage(army)
    assert result.average_test_pass_probability == Fraction(21, 36)
    assert result.assumes_stand_fast is False
    assert result.assumes_positional_support is False


def test_aggregation_retains_exact_probability_until_presentation():
    army = make_army((make_profile("NORMAL"), 1))
    result = aggregate_army_courage(army)
    assert isinstance(result.average_test_pass_probability, Fraction)
    assert isinstance(result.expected_passes_per_test_window, Fraction)


def test_only_fielded_models_are_counted_in_average():
    army = make_army((make_profile("NORMAL"), 2))
    assert aggregate_army_courage(army).model_count == army.model_count()
