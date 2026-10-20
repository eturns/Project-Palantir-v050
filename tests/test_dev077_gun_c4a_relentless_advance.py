from fractions import Fraction
from types import SimpleNamespace
import pytest
from gundabad_relentless_advance import FriendlyContact, resolve_relentless_advance
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from configured_profile import ConfiguredProfile


def _ogre():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    return ConfiguredProfile(profiles['GUNDABAD_OGRE'])


def _friend(race='ORC', defence=4, overlap=False):
    return FriendlyContact('friend1', frozenset({race}), defence, overlap)


def test_charge_hit_is_strength_three():
    outcome, = resolve_relentless_advance(_ogre(), (_friend(),), charging_into_combat=True)
    assert outcome.strength == 3
    assert outcome.wound_probability == Fraction(1, 3)
    assert not outcome.automatically_slain


@pytest.mark.parametrize('race', ['ORC', 'GOBLIN', 'BAT'])
def test_allowed_friendly_races(race):
    assert len(resolve_relentless_advance(_ogre(), (_friend(race),), charging_into_combat=True)) == 1


def test_final_overlap_automatically_slays():
    outcome, = resolve_relentless_advance(_ogre(), (_friend(overlap=True),), charging_into_combat=True)
    assert outcome.automatically_slain


def test_no_permission_for_normal_or_enemy_forced_movement():
    ogre = _ogre()
    assert resolve_relentless_advance(ogre, (_friend(),), charging_into_combat=False) == ()
    assert resolve_relentless_advance(ogre, (_friend(),), charging_into_combat=True, forced_by_enemy_effect=True) == ()


def test_no_permission_for_unrelated_models():
    model = SimpleNamespace(profile=SimpleNamespace(id='WAR_BAT'), effective_special_rules=())
    assert resolve_relentless_advance(model, (_friend(),), charging_into_combat=True) == ()


def test_invalid_path_race_and_duplicates_rejected():
    with pytest.raises(ValueError, match='race'):
        resolve_relentless_advance(_ogre(), (_friend('DWARF'),), charging_into_combat=True)
    with pytest.raises(ValueError, match='Duplicate'):
        resolve_relentless_advance(_ogre(), (_friend(), _friend()), charging_into_combat=True)
    with pytest.raises(ValueError, match='defence'):
        FriendlyContact('x', frozenset({'ORC'}), 11)
