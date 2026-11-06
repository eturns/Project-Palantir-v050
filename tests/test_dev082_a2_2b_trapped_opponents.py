"""DEV-082-A2-2B: explicit trapping in isolated Offence evidence.
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


def attacker(*, attacks=1, cavalry=False, savage=False, backstabbers=False):
    profile = Profile(
        id='DEV082_TRAP_ATTACKER', name='Trapping test', points=20,
        movement=6, fight=4, shooting='4+', strength=4, defence=5,
        attacks=attacks, wounds=1, courage='4+', intelligence='4+',
        might=0, will=0, fate=0, max_in_army=1,
        model_types={ModelType.CAVALRY if cavalry else ModelType.INFANTRY},
    )
    for identifier, present in (('SAVAGE_HUNTERS', savage), ('BACKSTABBERS', backstabbers)):
        if present:
            profile.special_rules.append(ProfileSpecialRuleAssignment(
                rule=SpecialRule(id=identifier, name=identifier, category=RuleCategory.SPECIAL),
            ))
    return ConfiguredProfile(profile=profile)


def test_trapped_target_increases_one_attack_elimination_chance():
    model = attacker()
    normal = calculate_charge_state_offence_evidence(model, defender_trapped=False)
    trapped = calculate_charge_state_offence_evidence(model, defender_trapped=True)
    # F4 A1 against F4 A1: duel win 1/2; S4 against D6 wounds on 5+.
    assert normal.uncharged == pytest.approx(1 / 6)
    assert trapped.uncharged == pytest.approx((1 / 2) * (1 - (2 / 3) ** 2))
    assert trapped.trap_context_status == 'explicit_trapped'


def test_trap_does_not_add_duel_dice(monkeypatch):
    import offence_charge_state_evidence as module
    original = module.calculate_configured_duel_probability
    calls = []

    def spy(*args, **kwargs):
        value = original(*args, **kwargs)
        calls.append(value.attacker_win_probability)
        return value

    monkeypatch.setattr(module, 'calculate_configured_duel_probability', spy)
    normal = calculate_charge_state_offence_evidence(attacker(attacks=2), defender_trapped=False)
    plain_duels = calls[:]
    calls.clear()
    trapped = calculate_charge_state_offence_evidence(attacker(attacks=2), defender_trapped=True)
    assert calls == pytest.approx(plain_duels)
    assert trapped.uncharged > normal.uncharged


def test_trap_doubles_final_charging_attacks_exactly_once(monkeypatch):
    import offence_charge_state_evidence as module
    original = module.get_wound_distribution
    strikes = []

    def spy(number_of_strikes, wound_probability):
        strikes.append(number_of_strikes)
        return original(number_of_strikes, wound_probability)

    monkeypatch.setattr(module, 'get_wound_distribution', spy)
    calculate_charge_state_offence_evidence(attacker(cavalry=True, savage=True), defender_trapped=True)
    assert strikes == [2, 4, 6]  # 1 base, +1 Savage, +1 eligible cavalry, then double


def test_trap_alone_does_not_infer_cavalry_bonus():
    result = calculate_charge_state_offence_evidence(attacker(cavalry=True), defender_trapped=True)
    assert result.uncharged == pytest.approx(result.charged_without_cavalry_bonus)
    assert result.charged_with_cavalry_bonus > result.charged_without_cavalry_bonus


def test_backstabbers_wound_bonus_requires_explicit_trapped_context():
    model = attacker(backstabbers=True)
    ordinary = calculate_charge_state_offence_evidence(model, defender_trapped=False)
    unknown = calculate_charge_state_offence_evidence(model)
    trapped = calculate_charge_state_offence_evidence(model, defender_trapped=True)
    assert ordinary.uncharged == pytest.approx(unknown.uncharged)
    assert trapped.uncharged > ordinary.uncharged
    assert unknown.trap_context_status == 'untrapped_reference_trap_unknown'


def test_explicit_false_matches_unchanged_default_but_records_status():
    model = attacker(savage=True)
    reference = calculate_charge_state_offence_evidence(model)
    known_not_trapped = calculate_charge_state_offence_evidence(model, defender_trapped=False)
    assert reference.uncharged == pytest.approx(known_not_trapped.uncharged)
    assert reference.charged_without_cavalry_bonus == pytest.approx(known_not_trapped.charged_without_cavalry_bonus)
    assert reference.charged_with_cavalry_bonus == pytest.approx(known_not_trapped.charged_with_cavalry_bonus)
    assert known_not_trapped.trap_context_status == 'explicit_not_trapped'


@pytest.mark.parametrize('value', [1, 0, 'True', [], 0.5])
def test_non_boolean_trap_context_is_rejected(value):
    with pytest.raises(TypeError, match='defender_trapped'):
        calculate_charge_state_offence_evidence(attacker(), defender_trapped=value)
