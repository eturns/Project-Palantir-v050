"""DEV-077-GT-C2C: source-verified King-only movement outcomes."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from gundabad_relentless_advance import (
    FriendlyContact, resolve_relentless_advance,
)
from goblin_king_relentless_advance import resolve_goblin_king_relentless_advance


@pytest.fixture(scope="module")
def models():
    profiles = {profile.id: profile for profile in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    return {key: ConfiguredProfile(profiles[key]) for key in
            ("GT_KING", "GT_WARRIOR", "GUNDABAD_OGRE")}


def contact(name="goblin-one", race="GOBLIN", defence=3, overlap=False):
    return FriendlyContact(name, frozenset({race}), defence, overlap)


def test_strength_three_and_canonical_wound_probability(models):
    (outcome,) = resolve_goblin_king_relentless_advance(
        models["GT_KING"], (contact(),), charging_into_combat=True)
    assert outcome.model_id == "goblin-one"
    assert outcome.strength == 3
    assert outcome.wound_probability == Fraction(1, 2)
    assert not outcome.automatically_slain


def test_final_overlap_automatically_slain(models):
    (outcome,) = resolve_goblin_king_relentless_advance(
        models["GT_KING"], (contact(overlap=True),), charging_into_combat=True)
    assert outcome.automatically_slain


def test_multiple_distinct_contacts(models):
    result = resolve_goblin_king_relentless_advance(
        models["GT_KING"], (contact(), contact("goblin-two", defence=4)),
        charging_into_combat=True)
    assert len(result) == 2
    assert result[1].wound_probability == Fraction(1, 3)


@pytest.mark.parametrize("race", ["ORC", "BAT", "DWARF", "HOBBIT"])
def test_cannot_move_through_non_goblins(models, race):
    with pytest.raises(ValueError, match="Goblins"):
        resolve_goblin_king_relentless_advance(
            models["GT_KING"], (contact(race=race),), charging_into_combat=True)


def test_non_charge_or_forced_movement_denied(models):
    king = models["GT_KING"]
    assert resolve_goblin_king_relentless_advance(
        king, (contact(),), charging_into_combat=False) == ()
    assert resolve_goblin_king_relentless_advance(
        king, (contact(),), charging_into_combat=True,
        forced_by_enemy_effect=True) == ()


def test_unrelated_profiles_cannot_use_kings_resolver(models):
    for key in ("GT_WARRIOR", "GUNDABAD_OGRE"):
        assert resolve_goblin_king_relentless_advance(
            models[key], (contact(),), charging_into_combat=True) == ()


def test_missing_rule_denies_use():
    model = SimpleNamespace(profile=SimpleNamespace(id="GT_KING"), effective_special_rules=())
    assert resolve_goblin_king_relentless_advance(
        model, (contact(),), charging_into_combat=True) == ()


def test_duplicate_contact_rejected(models):
    with pytest.raises(ValueError, match="Duplicate"):
        resolve_goblin_king_relentless_advance(
            models["GT_KING"], (contact(), contact()), charging_into_combat=True)


def test_bad_contact_type_rejected(models):
    with pytest.raises(TypeError, match="FriendlyContact"):
        resolve_goblin_king_relentless_advance(
            models["GT_KING"], ("goblin",), charging_into_combat=True)


@pytest.mark.parametrize("flag", [None, 1, "yes"])
def test_invalid_charge_flag_rejected(models, flag):
    with pytest.raises(TypeError, match="flags"):
        resolve_goblin_king_relentless_advance(
            models["GT_KING"], (contact(),), charging_into_combat=flag)


def test_existing_ogre_mechanics_remain_separate(models):
    ogre = models["GUNDABAD_OGRE"]
    (result,) = resolve_relentless_advance(
        ogre, (contact(race="ORC", defence=4),), charging_into_combat=True)
    assert result.strength == 3
    assert result.wound_probability == Fraction(1, 3)


def test_no_automatic_geometry_or_state_mutation(models):
    empty = resolve_goblin_king_relentless_advance(
        models["GT_KING"], (), charging_into_combat=True)
    assert empty == ()
