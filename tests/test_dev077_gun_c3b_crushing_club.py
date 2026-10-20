import pytest
from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from profile_option_loader import load_profile_options, build_profile_options_by_external_id
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from melee_weapon_selection import MeleeWeaponSelection
from special_rule_strike_damage import get_special_rule_strike_damage
from gundabad_crushing_club import crushing_club_knockdown, crushing_club_strike_damage, uses_crushing_club


@pytest.fixture(scope="module")
def configured():
    profiles = {p.id: p for p in load_all_profiles()}
    options = load_profile_options(profiles)
    gear = load_wargear()
    load_profile_default_wargear(profiles, gear)
    load_profile_option_wargear_assignments(options, gear)
    external = build_profile_options_by_external_id(options)
    return (
        ConfiguredProfile(profiles["GUNDABAD_TROLL"]),
        ConfiguredProfile(profiles["GUNDABAD_TROLL"], selected_options=(external["OPT0677"],)),
        ConfiguredProfile(profiles["GUNDABAD_ORC_CAPTAIN"]),
    )


def test_club_damage_and_scythe_exclusion(configured):
    club, scythes, other = configured
    assert uses_crushing_club(club)
    assert not uses_crushing_club(scythes)
    assert not uses_crushing_club(other)
    assert crushing_club_strike_damage(club).wounds_per_successful_strike == 2
    assert crushing_club_strike_damage(scythes) is None
    assert get_special_rule_strike_damage(club).wounds_per_successful_strike == 2
    assert get_special_rule_strike_damage(scythes).wounds_per_successful_strike == 1


def test_selected_weapon_controls_damage(configured):
    club, _, _ = configured
    assert uses_crushing_club(club, MeleeWeaponSelection("WG_CRUSHING_CLUB"))
    assert not uses_crushing_club(club, MeleeWeaponSelection("WG_HAND_WEAPON"))


def test_knockdown_on_three_plus(configured):
    club, _, _ = configured
    event = crushing_club_knockdown(club, struck=True, slain=False)
    assert [event.resolve(n) for n in range(1, 7)] == [False, False, True, True, True, True]


def test_knockdown_only_for_unslain_struck_target(configured):
    club, scythes, _ = configured
    for attacker, struck, slain in [(club, True, True), (club, False, False), (scythes, True, False)]:
        assert not crushing_club_knockdown(attacker, struck=struck, slain=slain).resolve(6)


def test_invalid_rolls_rejected(configured):
    club, _, _ = configured
    event = crushing_club_knockdown(club, struck=True, slain=False)
    for value in (0, 7, True, 2.5):
        with pytest.raises(ValueError):
            event.resolve(value)
