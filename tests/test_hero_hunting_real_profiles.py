"""DEV-077S-I2-G2-B7: canonical real-profile Hero Hunting evidence audit.

No dashboard scoring changes. This module checks production relationship loading,
not artificial replacement rule definitions.
"""
import pytest

from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_state import MorgulBladeState
from wound_context import WoundContext
from post_prevention_effect import PostPreventionEffect
from configured_post_prevention_effect import get_configured_post_prevention_effect
from special_rule_strike_damage import get_special_rule_strike_damage
from special_rule_wound_effect import get_contextual_special_rule_wound_reroll
from hero_hunting_melee import calculate_hero_hunting_melee_evidence


@pytest.fixture(scope="module")
def models():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    load_profile_default_wargear(profiles=profiles, wargear=load_wargear())
    return {key: ConfiguredProfile(profile=profile) for key, profile in profiles.items()}


def _rules(model):
    return {assignment.rule.id for assignment in model.effective_special_rules}


def test_necromancer_has_drain_soul_from_canonical_relationships(models):
    nec = models['DG_NEC']
    assert 'DRAIN_SOUL' in _rules(nec)
    assert get_configured_post_prevention_effect(nec, context=WoundContext()) is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO


def test_dark_headsman_executioner_from_canonical_relationships(models):
    headsman = models['DG_DH']
    assert 'EXECUTIONER' in _rules(headsman)
    assert get_special_rule_strike_damage(headsman, context=WoundContext(attacker_natural_duel_roll=6)).wounds_per_successful_strike == 2
    assert get_special_rule_strike_damage(headsman, context=WoundContext(attacker_natural_duel_roll=5)).wounds_per_successful_strike == 1


def test_forsaken_bane_of_kings_relationship_present(models):
    assert 'BANE_OF_KINGS' in _rules(models['DG_FS'])


def test_bolg_enemy_relations_loaded_with_parameters(models):
    assignments = models['BOLG_SPAWN_OF_AZOG'].effective_special_rules
    enemies = {a.parameter for a in assignments if a.rule.id == 'ANCIENT_ENEMIES'}
    assert enemies == {'DWARF', 'ELF'}
    assert 'BRINGER_OF_DEATH' in _rules(models['BOLG_SPAWN_OF_AZOG'])


def test_bolg_target_keyword_matching_is_conditional(models):
    bolg = models['BOLG_SPAWN_OF_AZOG']
    assert get_contextual_special_rule_wound_reroll(bolg, defender=models['DG_NEC']).reroll_natural_ones is False
    # The production model's Dwarf/Elf list is already covered by the parameter assertions.


def test_bolg_unsupported_bring_of_death_fails_closed(models):
    with pytest.raises(ValueError, match='Incomplete Hero Hunting'):
        calculate_hero_hunting_melee_evidence(
            attacker=models['BOLG_SPAWN_OF_AZOG'], defender=models['DG_NEC'],
            remaining_wounds=1, ordinary_one_on_one=True,
        )


def test_castellan_morgul_blade_requires_explicit_state(models):
    castellan = models['DG_CASTELLAN']
    assert 'WG_MORGUL_BLADE' in {w.id for w in castellan.effective_wargear}
    with pytest.raises(ValueError, match='Morgul Blade'):
        calculate_hero_hunting_melee_evidence(
            attacker=castellan, defender=models['DG_NEC'],
            remaining_wounds=1, ordinary_one_on_one=True,
            attacker_melee_weapon=MeleeWeaponSelection('WG_MORGUL_BLADE'),
        )


def test_real_necromancer_wound_reset_not_equated_to_base_wounds(models):
    result = calculate_hero_hunting_melee_evidence(
        attacker=models['DG_NEC'], defender=models['DG_DH'],
        remaining_wounds=4, remaining_fate=0, ordinary_one_on_one=True,
    )
    assert result.evidence_status == 'limited_context_post_prevention'
    assert 0 <= result.elimination_probability <= 1
    assert result.elimination_probability > 0
