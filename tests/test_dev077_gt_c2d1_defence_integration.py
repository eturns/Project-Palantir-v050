"""DEV-077-GT-C2D1 integration: real Goblin-town models and defensive provenance."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from goblin_king_defence_integration import (
    BlubberyAttackContext, calculate_goblin_king_defence_evidence,
)
from loader import load_all_profiles
from rule_loader import load_special_rules
from relationship_loader import load_profile_special_rules
from configured_profile import ConfiguredProfile


@pytest.fixture(scope="module")
def profiles():
    profiles={p.id:p for p in load_all_profiles()}
    load_profile_special_rules(profiles,load_special_rules())
    return profiles


def army(*configured):
    models=[SimpleNamespace(configured_profile=p) for p in configured]
    return SimpleNamespace(fielded_models=lambda: tuple(models))


def test_production_registered_king_and_normal_hit(profiles):
    result=calculate_goblin_king_defence_evidence(
        army(ConfiguredProfile(profiles["GT_KING"])),
        attack_contexts=(BlubberyAttackContext(False,False,False),),
    )
    assert result.profile_id == "GT_KING"
    assert result.expected_wounds_remaining == Fraction(1,3)
    assert result.wound_prevention[0].prevention_target == 3


def test_elven_missile_and_exceptions(profiles):
    contexts=(
        BlubberyAttackContext(False,False,True),
        BlubberyAttackContext(False,True,False),
        BlubberyAttackContext(True,False,False),
    )
    r=calculate_goblin_king_defence_evidence(
        army(ConfiguredProfile(profiles["GT_KING"])),attack_contexts=contexts)
    assert tuple(x.wound_remaining_probability for x in r.wound_prevention)==(
        Fraction(1,2), Fraction(1), Fraction(1))


def test_does_not_invent_attack_context(profiles):
    r=calculate_goblin_king_defence_evidence(
        army(ConfiguredProfile(profiles["GT_KING"])),attack_contexts=())
    assert r.contexts_supplied == 0
    assert r.expected_wounds_remaining == 0


def test_cross_army_returns_none(profiles):
    r=calculate_goblin_king_defence_evidence(
        army(ConfiguredProfile(profiles["GUNDABAD_OGRE"])),
        attack_contexts=())
    assert r is None


def test_rejects_unsupported_input(profiles):
    with pytest.raises(TypeError):
        calculate_goblin_king_defence_evidence(
            army(ConfiguredProfile(profiles["GT_KING"])),attack_contexts=(None,))


def test_rejects_duplicate_kings(profiles):
    king=ConfiguredProfile(profiles["GT_KING"])
    with pytest.raises(ValueError,match="exactly one"):
        calculate_goblin_king_defence_evidence(
            army(king,king),attack_contexts=())
