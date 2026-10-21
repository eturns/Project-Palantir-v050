"""DEV-077-GT-C2D3: verified fielded contacts and friendly loss evidence."""
from fractions import Fraction
from types import SimpleNamespace
import pytest

from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from gundabad_relentless_advance import FriendlyContact
from goblin_king_relentless_advance_army_evidence import (
    ChargePathContext, assess_army_relentless_advance,
)


@pytest.fixture(scope="module")
def profiles():
    profiles={p.id:p for p in load_all_profiles()}
    load_profile_special_rules(profiles,load_special_rules())
    return {key:ConfiguredProfile(profiles[key]) for key in
            ("GT_KING","GT_WARRIOR","GUNDABAD_OGRE")}


def roster(profiles, include_king=True, include_warrior=True):
    entries=[]
    if include_king:
        entries.append(SimpleNamespace(id="king1",configured_profile=profiles["GT_KING"]))
    if include_warrior:
        entries.append(SimpleNamespace(id="goblin1",configured_profile=profiles["GT_WARRIOR"]))
    return SimpleNamespace(fielded_models=lambda:tuple(entries))


def context(profiles, overlap=False, race="GOBLIN", defence=None,
            charge=True, forced=False):
    if defence is None:
        defence=profiles["GT_WARRIOR"].effective_defence
    return ChargePathContext((FriendlyContact(
        "goblin1",frozenset({race}),defence,overlap),),charge,forced)


def test_absent_context_is_unknown(profiles):
    (e,)=assess_army_relentless_advance(
        army=roster(profiles),contexts_by_king_id={})
    assert not e.context_supplied and e.charge_permitted is None
    assert e.expected_friendly_hit_wounds is None
    assert e.expected_enemy_wounds is None


def test_confirmed_contact_records_friendly_cost_not_enemy_offence(profiles):
    (e,)=assess_army_relentless_advance(
        army=roster(profiles),contexts_by_king_id={"king1":context(profiles)})
    assert e.charge_permitted
    assert len(e.contact_outcomes)==1
    assert e.contact_outcomes[0].strength == 3
    assert e.expected_friendly_hit_wounds == e.contact_outcomes[0].wound_probability
    assert e.expected_enemy_wounds is None


def test_overlap_kills_roster_goblin(profiles):
    (e,)=assess_army_relentless_advance(
        army=roster(profiles),contexts_by_king_id={"king1":context(profiles,overlap=True)})
    assert e.automatically_slain_friendly_model_ids==("goblin1",)


@pytest.mark.parametrize("charge,forced",[(False,False),(True,True)])
def test_non_charge_and_enemy_forced_movement(profiles,charge,forced):
    (e,)=assess_army_relentless_advance(
        army=roster(profiles),contexts_by_king_id={
            "king1":context(profiles,charge=charge,forced=forced)})
    assert e.charge_permitted is False
    assert e.contact_outcomes==()
    assert e.expected_friendly_hit_wounds==0


def test_missing_friendly_model_rejected(profiles):
    with pytest.raises(ValueError,match="fielded friendly"):
        assess_army_relentless_advance(
            army=roster(profiles,include_warrior=False),contexts_by_king_id={
                "king1":context(profiles)})


def test_contact_cannot_claim_different_defence(profiles):
    with pytest.raises(ValueError,match="Defence"):
        assess_army_relentless_advance(
            army=roster(profiles),contexts_by_king_id={
                "king1":context(profiles,defence=10)})


def test_cannot_pass_through_other_race(profiles):
    with pytest.raises(ValueError,match="contradicts"):
        assess_army_relentless_advance(
            army=roster(profiles),contexts_by_king_id={
                "king1":context(profiles,race="ORC")})


def test_unrelated_army_has_no_king_evidence(profiles):
    assert assess_army_relentless_advance(
        army=roster(profiles,include_king=False),contexts_by_king_id={})==()


def test_unknown_king_context_rejected(profiles):
    with pytest.raises(ValueError,match="unknown/non-King"):
        assess_army_relentless_advance(
            army=roster(profiles),contexts_by_king_id={"notking":context(profiles)})


def test_context_type_rejected(profiles):
    with pytest.raises(TypeError,match="ChargePathContext"):
        assess_army_relentless_advance(
            army=roster(profiles),contexts_by_king_id={"king1":None})


def test_does_not_mutate_roster(profiles):
    a=roster(profiles)
    original=a.fielded_models()
    assess_army_relentless_advance(
        army=a,contexts_by_king_id={"king1":context(profiles,overlap=True)})
    assert a.fielded_models()==original
