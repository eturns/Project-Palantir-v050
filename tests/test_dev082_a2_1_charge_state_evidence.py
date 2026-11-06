"""DEV-082-A2-1 — opt-in diagnostic acceptance tests.

Author: Edward Turns (Project Lead)
"""
import pytest

from configured_profile import ConfiguredProfile
from database.rule_category import RuleCategory
from profile_classification import ModelType
from profile_special_rule_assignment import ProfileSpecialRuleAssignment
from profiles import Profile
from special_rule import SpecialRule
from offence_charge_state_evidence import calculate_charge_state_offence_evidence
from army_offence_capability import calculate_army_offensive_output_density
from army import Army


def make_attacker(*, cavalry=False, savage=False, talons=False):
    profile = Profile(
        id='DEV082_ATTACKER', name='Test attacker', points=20,
        movement=6, fight=4, shooting='4+', strength=4, defence=5,
        attacks=1, wounds=1, courage='4+', intelligence='4+',
        might=0, will=0, fate=0, max_in_army=1,
        model_types={ModelType.CAVALRY if cavalry else ModelType.INFANTRY},
    )
    for rule_id in ('SAVAGE_HUNTERS' if savage else None, 'PIERCING_TALONS' if talons else None):
        if rule_id:
            profile.special_rules.append(ProfileSpecialRuleAssignment(
                rule=SpecialRule(id=rule_id, name=rule_id, category=RuleCategory.SPECIAL),
            ))
    return ConfiguredProfile(profile=profile)


def test_plain_infantry_has_same_output_in_all_states():
    result = calculate_charge_state_offence_evidence(make_attacker())
    assert result.uncharged == pytest.approx(result.charged_without_cavalry_bonus)
    assert result.uncharged == pytest.approx(result.charged_with_cavalry_bonus)
    assert result.weighted is None


def test_savage_hunters_extra_strike_changes_elimination_not_just_duel():
    result = calculate_charge_state_offence_evidence(make_attacker(savage=True))
    assert result.charged_without_cavalry_bonus > result.uncharged
    assert result.charged_without_cavalry_bonus == pytest.approx(result.charged_with_cavalry_bonus)


def test_cavalry_bonus_affects_same_state_strikes_and_duel():
    result = calculate_charge_state_offence_evidence(make_attacker(cavalry=True))
    assert result.charged_with_cavalry_bonus > result.charged_without_cavalry_bonus
    assert result.charged_without_cavalry_bonus == pytest.approx(result.uncharged)


def test_mounted_savage_hunters_stack_only_eligible_bonuses():
    result = calculate_charge_state_offence_evidence(make_attacker(cavalry=True, savage=True))
    assert result.uncharged < result.charged_without_cavalry_bonus
    assert result.charged_without_cavalry_bonus < result.charged_with_cavalry_bonus


def test_piercing_talons_only_applies_when_charged():
    result = calculate_charge_state_offence_evidence(make_attacker(talons=True))
    assert result.charged_without_cavalry_bonus > result.uncharged


def test_explicit_probabilities_mix_complete_state_outputs():
    result = calculate_charge_state_offence_evidence(
        make_attacker(cavalry=True, savage=True),
        charge_probability=0.4, cavalry_eligibility_probability=0.25,
    )
    expected = (0.6*result.uncharged
                + 0.4*(0.75*result.charged_without_cavalry_bonus
                       + 0.25*result.charged_with_cavalry_bonus))
    assert result.weighted == pytest.approx(expected)


def test_missing_eligibility_never_invents_weighted_probability():
    result = calculate_charge_state_offence_evidence(
        make_attacker(cavalry=True), charge_probability=0.5,
    )
    assert result.weighted is None


@pytest.mark.parametrize('value', [-0.01, 1.01, float('nan'), float('inf')])
def test_invalid_probabilities_are_rejected(value):
    with pytest.raises(ValueError):
        calculate_charge_state_offence_evidence(make_attacker(), charge_probability=value)


def test_existing_army_score_is_not_replaced_by_diagnostic():
    attacker = make_attacker(cavalry=True, savage=True)
    army = Army()
    army.add_profile(attacker.profile, quantity=1)
    baseline = calculate_army_offensive_output_density(army)
    calculate_charge_state_offence_evidence(attacker)
    assert calculate_army_offensive_output_density(army) == pytest.approx(baseline)
