"""DEV-077-GUN-C5-A: source-verified restricted support tests."""
import pytest

from chittering_hordes_support import (
    can_chittering_hordes_support,
    has_chittering_hordes,
    make_chittering_hordes_support_participant,
)
from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from profile_option_loader import load_profile_options
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from melee_weapon_selection import MeleeWeaponSelection


def _models():
    profiles = {profile.id: profile for profile in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    options = load_profile_options(profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles, wargear)
    load_profile_option_wargear_assignments(options, wargear)
    return profiles


def test_rule_registered_for_goblin_mercenary_and_captain():
    models = _models()
    assert has_chittering_hordes(ConfiguredProfile(models["GOBLIN_MERCENARY"]))
    assert has_chittering_hordes(ConfiguredProfile(models["GOBLIN_MERCENARY_CAPTAIN"]))


def test_support_between_chittering_hordes_models_contributes_one_duel_die_only():
    models = _models()
    goblin = ConfiguredProfile(models["GOBLIN_MERCENARY"])
    captain = ConfiguredProfile(models["GOBLIN_MERCENARY_CAPTAIN"])
    support = make_chittering_hordes_support_participant(
        goblin, captain, valid_support_position=True,
    )
    assert support.duel_dice == 1
    assert support.contributes_fight
    assert not support.can_make_strikes
    assert support.profile.id == "GOBLIN_MERCENARY"


def test_rejects_support_of_model_without_rule():
    models = _models()
    goblin = ConfiguredProfile(models["GOBLIN_MERCENARY"])
    ogre = ConfiguredProfile(models["GUNDABAD_OGRE"])
    assert not can_chittering_hordes_support(
        goblin, ogre, valid_support_position=True,
    )
    assert not can_chittering_hordes_support(
        ogre, goblin, valid_support_position=True,
    )


def test_position_must_be_explicitly_legal():
    models = _models()
    goblin = ConfiguredProfile(models["GOBLIN_MERCENARY"])
    assert not can_chittering_hordes_support(
        goblin, goblin, valid_support_position=False,
    )
    with pytest.raises(TypeError):
        can_chittering_hordes_support(goblin, goblin, valid_support_position=None)


def test_cannot_support_with_unowned_weapon():
    models = _models()
    goblin = ConfiguredProfile(models["GOBLIN_MERCENARY"])
    with pytest.raises(ValueError, match="not held"):
        can_chittering_hordes_support(
            goblin, goblin, valid_support_position=True,
            selected_weapon=MeleeWeaponSelection("NOT_OWNED"),
        )


def test_unpermitted_support_construction_fails_closed():
    models = _models()
    goblin = ConfiguredProfile(models["GOBLIN_MERCENARY"])
    with pytest.raises(ValueError, match="not permitted"):
        make_chittering_hordes_support_participant(
            goblin, goblin, valid_support_position=False,
        )
