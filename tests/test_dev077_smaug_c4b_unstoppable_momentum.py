"""DEV-077-SMAUG-C4B/E isolated Unstoppable Momentum regression."""
from fractions import Fraction
import pytest
from smaug_unstoppable_momentum import (
    EngagedDefender, calculate_unstoppable_momentum,
)


def calculate(*defenders, has_unstoppable_momentum=True):
    return calculate_unstoppable_momentum(
        attacker_profile_id="SMAUG", has_unstoppable_momentum=has_unstoppable_momentum,
        won_duel=True, engaged_defenders=tuple(defenders),
    )


def test_one_strength_nine_hit_for_every_engaged_defender():
    result = calculate(EngagedDefender("a", 5), EngagedDefender("b", 8), EngagedDefender("c", 10))
    assert result.momentum_hits == 3
    assert [r.hit_count for r in result.target_evidence] == [1, 1, 1]


def test_correct_wound_table_and_exact_expectation():
    result = calculate(EngagedDefender("a", 5), EngagedDefender("b", 10))
    assert result.target_evidence[0].wound_probability == Fraction(4, 6)
    assert result.target_evidence[1].wound_probability == Fraction(2, 6)
    assert result.expected_wounds == Fraction(6, 6)


def test_alternative_attack_does_not_add_four_normal_strikes():
    result = calculate(EngagedDefender("a", 5), EngagedDefender("b", 5))
    assert result.replaces_normal_strikes
    assert result.normal_strikes_allocated == 0
    assert result.momentum_hits == 2


def test_single_hit_cannot_slay_two_wound_defender_without_other_mechanics():
    result = calculate(EngagedDefender("hero", 5, remaining_wounds=2))
    assert result.target_evidence[0].probability_slaying_before_prevention == 0


def test_rule_requires_won_duel():
    with pytest.raises(ValueError, match="won the Duel"):
        calculate_unstoppable_momentum(attacker_profile_id="SMAUG", has_unstoppable_momentum=True,
                                       won_duel=False, engaged_defenders=(EngagedDefender("a", 5),))


def test_non_smaug_excluded():
    with pytest.raises(ValueError, match="restricted"):
        calculate_unstoppable_momentum(attacker_profile_id="TT_BILL", has_unstoppable_momentum=True,
                                       won_duel=True, engaged_defenders=(EngagedDefender("a", 5),))


def test_missing_rule_rejected():
    with pytest.raises(ValueError, match="does not possess"):
        calculate(EngagedDefender("a", 5), has_unstoppable_momentum=False)


def test_duplicate_engaged_model_rejected():
    with pytest.raises(ValueError, match="unique"):
        calculate(EngagedDefender("a", 5), EngagedDefender("a", 5))


def test_invalid_defence_rejected():
    with pytest.raises(ValueError, match="Defence"):
        calculate(EngagedDefender("a", 11))


def test_no_dashboard_or_scenario_contamination():
    evidence = calculate(EngagedDefender("a", 5))
    assert evidence.dashboard_score is None and evidence.scenario_score is None
