"""DEV-077-GUN-C3-C: Scythe Gauntlets configured combat mechanics."""
import pytest

from loader import load_all_profiles
from configured_profile import ConfiguredProfile
from profile_option_loader import load_profile_options, build_profile_options_by_external_id
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from wargear_loader import load_wargear
from special_rule_strike_damage import get_special_rule_strike_damage
from gundabad_crushing_club import crushing_club_knockdown
from configured_duel_probability import calculate_configured_duel_probability


def _profiles():
    profiles = {p.id: p for p in load_all_profiles()}
    options = load_profile_options(profiles=profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_option_wargear_assignments(profile_options=options, wargear=wargear)
    external = build_profile_options_by_external_id(options)
    troll = profiles['GUNDABAD_TROLL']
    return (ConfiguredProfile(profile=troll),
            ConfiguredProfile(profile=troll, selected_options=(external['OPT0677'],)))


def test_equipment_replaces_club_without_changing_canonical_profile():
    club, scythes = _profiles()
    assert 'WG_CRUSHING_CLUB' in {w.id for w in club.effective_wargear}
    ids = {w.id for w in scythes.effective_wargear}
    assert 'WG_SCYTHE_GAUNTLETS' in ids
    assert 'WG_CRUSHING_CLUB' not in ids
    assert scythes.profile.attacks == 3
    assert club.profile.attacks == 3


def test_scythes_raise_only_configured_attacks():
    club, scythes = _profiles()
    assert club.effective_attacks == 3
    assert scythes.effective_attacks == 4
    assert scythes.points == club.points + 10


def test_scythes_remove_club_damage_and_knockdown():
    club, scythes = _profiles()
    assert get_special_rule_strike_damage(club).wounds_per_successful_strike == 2
    assert get_special_rule_strike_damage(scythes).wounds_per_successful_strike == 1
    assert crushing_club_knockdown(club, struck=True, slain=False).resolve(3)
    assert not crushing_club_knockdown(scythes, struck=True, slain=False).resolve(6)


def test_extra_attack_reaches_duel_resolver():
    club, scythes = _profiles()
    # Self-matches keep all combat attributes equal except the option's Attacks.
    normal = calculate_configured_duel_probability(attacker=club, defender=club)
    boosted = calculate_configured_duel_probability(attacker=scythes, defender=club)
    assert boosted.attacker_win_probability > normal.attacker_win_probability


def test_no_cross_profile_attack_changes():
    profiles = {p.id: p for p in load_all_profiles()}
    captain = ConfiguredProfile(profile=profiles['GUNDABAD_ORC_CAPTAIN'])
    assert captain.effective_attacks == captain.profile.attacks
