"""DEV-077-GUN-C3-D: charge-dependent War Bat wound modifiers."""
import csv
from pathlib import Path

import pytest

from configured_profile import ConfiguredProfile
from configured_wound_probability import calculate_configured_wound_probability
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from special_rule_wound_modifier import get_special_rule_wound_modifiers
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


def _models():
    profiles = {profile.id: profile for profile in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    bat = ConfiguredProfile(profile=profiles['WAR_BAT'])
    defender = ConfiguredProfile(profile=profiles['GUNDABAD_ORC_CAPTAIN'])
    unrelated = ConfiguredProfile(profile=profiles['GUNDABAD_OGRE'])
    return bat, defender, unrelated


def test_registered_on_war_bat_only():
    with Path('data/profiles/profile_special_rules.csv').open(newline='', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))
    assignments = [row['profile_id'] for row in rows if row['rule_id'] == 'PIERCING_TALONS']
    assert assignments == ['WAR_BAT']


def test_charge_adds_exactly_one_wound_modifier():
    bat, defender, _ = _models()
    bonus = get_special_rule_wound_modifiers(bat, defender, WoundContext(attacker_charged=True))
    assert len(bonus) == 1
    assert bonus[0].to_wound == 1


def test_no_bonus_if_not_charging_or_unknown():
    bat, defender, _ = _models()
    for context in (None, WoundContext(), WoundContext(attacker_charged=False)):
        assert not get_special_rule_wound_modifiers(bat, defender, context)


def test_no_bonus_for_ranged_wounds_or_other_models():
    bat, defender, unrelated = _models()
    assert not get_special_rule_wound_modifiers(
        bat, defender, WoundContext(attacker_charged=True, attack_type=WoundAttackType.SHOOTING)
    )
    assert not get_special_rule_wound_modifiers(
        unrelated, defender, WoundContext(attacker_charged=True)
    )


def test_charging_increases_canonical_wound_probability():
    bat, defender, _ = _models()
    baseline = calculate_configured_wound_probability(bat, defender, context=WoundContext(attacker_charged=False))
    charged = calculate_configured_wound_probability(bat, defender, context=WoundContext(attacker_charged=True))
    assert charged > baseline
    assert charged <= 1


@pytest.mark.parametrize('invalid', [1, 'yes', [], 0.0])
def test_charge_evidence_requires_bool_or_none(invalid):
    with pytest.raises(TypeError):
        WoundContext(attacker_charged=invalid)
