"""DEV-082-A2-2A — isolated melee weapon selection checks.
Author: Edward Turns (Project Lead)
"""
import pytest
from configured_profile import ConfiguredProfile
from profiles import Profile
from wargear import Wargear
from melee_weapon_selection import MeleeWeaponSelection
from offence_charge_state_evidence import calculate_charge_state_offence_evidence


def make_attacker():
    profile = Profile(
        id='DEV082_WEAPON', name='Weapon tester', points=25,
        movement=6, fight=4, shooting='4+', strength=4, defence=5,
        attacks=1, wounds=1, courage='4+', intelligence='4+',
        might=0, will=0, fate=0, max_in_army=1,
    )
    profile.default_wargear.extend((
        Wargear(id='WG_TWO_HANDED_WEAPON', name='Two-handed weapon'),
        Wargear(id='WG_SWORD', name='Sword'),
    ))
    return ConfiguredProfile(profile=profile)


def test_explicit_two_handed_weapon_changes_both_duel_and_wound_outcome():
    attacker = make_attacker()
    sword = calculate_charge_state_offence_evidence(
        attacker, attacker_selection=MeleeWeaponSelection('WG_SWORD'))
    two_handed = calculate_charge_state_offence_evidence(
        attacker, attacker_selection=MeleeWeaponSelection('WG_TWO_HANDED_WEAPON'))
    assert sword.uncharged != pytest.approx(two_handed.uncharged)
    assert sword.selected_weapon_id == 'WG_SWORD'
    assert two_handed.selected_weapon_id == 'WG_TWO_HANDED_WEAPON'
    assert sword.weapon_selection_status == 'explicit_owned_weapon'


def test_implicit_selection_preserves_prior_default_and_marks_provenance():
    attacker = make_attacker()
    result = calculate_charge_state_offence_evidence(attacker)
    assert result.weapon_selection_status == 'implicit_existing_resolver'
    assert result.selected_weapon_id is None
    assert result.uncharged == pytest.approx(
        calculate_charge_state_offence_evidence(
            attacker, attacker_selection=MeleeWeaponSelection('WG_TWO_HANDED_WEAPON')
        ).uncharged
    )


def test_invalid_weapon_refused():
    with pytest.raises(ValueError, match='not held'):
        calculate_charge_state_offence_evidence(
            make_attacker(), attacker_selection=MeleeWeaponSelection('NOT_OWNED'))


def test_invalid_selection_type_refused():
    with pytest.raises(TypeError, match='MeleeWeaponSelection'):
        calculate_charge_state_offence_evidence(make_attacker(), attacker_selection='WG_SWORD')


def test_result_remains_conditional_and_unrated():
    result = calculate_charge_state_offence_evidence(
        make_attacker(), attacker_selection=MeleeWeaponSelection('WG_SWORD'))
    assert result.weighted is None
    assert result.status == 'conditional_display_only_not_calibrated'


def test_selected_weapon_passes_through_every_combat_resolver(monkeypatch):
    import offence_charge_state_evidence as m
    attacker = make_attacker()
    choice = MeleeWeaponSelection('WG_SWORD')
    captured = {'duel': [], 'attacks': [], 'wound': [], 'damage': []}
    duel, attacks, wound, damage = (
        m.calculate_configured_duel_probability,
        m.get_effective_attacks,
        m.calculate_configured_wound_probability,
        m.get_special_rule_strike_damage,
    )

    def wrap_duel(*args, **kwargs):
        captured['duel'].append(kwargs.get('attacker_selection'))
        return duel(*args, **kwargs)

    def wrap_attacks(*args, **kwargs):
        captured['attacks'].append(kwargs.get('selection'))
        return attacks(*args, **kwargs)

    def wrap_wound(*args, **kwargs):
        captured['wound'].append(kwargs.get('attacker_selection'))
        return wound(*args, **kwargs)

    def wrap_damage(*args, **kwargs):
        captured['damage'].append(kwargs.get('selection'))
        return damage(*args, **kwargs)

    monkeypatch.setattr(m, 'calculate_configured_duel_probability', wrap_duel)
    monkeypatch.setattr(m, 'get_effective_attacks', wrap_attacks)
    monkeypatch.setattr(m, 'calculate_configured_wound_probability', wrap_wound)
    monkeypatch.setattr(m, 'get_special_rule_strike_damage', wrap_damage)
    calculate_charge_state_offence_evidence(attacker, attacker_selection=choice)
    for key, received in captured.items():
        assert received == [choice] * 3, key
