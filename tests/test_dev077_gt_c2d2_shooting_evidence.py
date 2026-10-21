"""DEV-077-GT-C2D2: fielded Goblin Projectile evidence, not scoring."""
from fractions import Fraction
from types import SimpleNamespace
import pytest
from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from goblin_king_projectile import ProjectileContext
from goblin_projectile_army_evidence import assess_army_goblin_projectile

@pytest.fixture(scope="module")
def profiles():
    return {p.id: ConfiguredProfile(p) for p in load_all_profiles()}

def army(profiles, *, with_king=True, with_donor=True):
    entries=[]
    if with_king:
        entries.append(SimpleNamespace(id="king-1",configured_profile=profiles["GT_KING"]))
    if with_donor:
        entries.append(SimpleNamespace(id="warrior-1",configured_profile=profiles["GT_WARRIOR"]))
    return SimpleNamespace(fielded_models=lambda:tuple(entries))

def context(**kw):
    values=dict(friendly_model_id="warrior-1",friendly_is_goblin=True,
                base_contact_confirmed=True,king_engaged=False,
                friendly_engaged=False,distance_inches=12,target_defence=6)
    values.update(kw)
    return ProjectileContext(**values)

def test_no_context_is_unknown_not_zero(profiles):
    (record,)=assess_army_goblin_projectile(
        army=army(profiles), contexts_by_king_id={})
    assert not record.context_supplied and record.eligible_attack is None
    assert record.expected_target_wounds is None

def test_real_king_and_goblin_donor(profiles):
    (record,)=assess_army_goblin_projectile(
        army=army(profiles),contexts_by_king_id={"king-1":context()})
    assert record.eligible_attack is True
    assert record.casualty_if_declared == "warrior-1"
    assert record.expected_target_hits==Fraction(1,3)
    assert record.expected_target_wounds==Fraction(2,9)
    assert record.projectile.prone_if_hit

def test_in_the_way_contributes(profiles):
    (record,)=assess_army_goblin_projectile(
        army=army(profiles),contexts_by_king_id={
            "king-1":context(in_the_way_required_rolls=(4,))})
    assert record.expected_target_hits==Fraction(1,6)

def test_ineligible_is_explicit_zero_not_unknown(profiles):
    (record,)=assess_army_goblin_projectile(
        army=army(profiles),contexts_by_king_id={
            "king-1":context(king_engaged=True)})
    assert record.context_supplied and record.eligible_attack is False
    assert record.expected_target_wounds==0 and record.projectile is None

def test_donor_must_exist(profiles):
    with pytest.raises(ValueError,match="distinct fielded"):
        assess_army_goblin_projectile(
            army=army(profiles,with_donor=False),
            contexts_by_king_id={"king-1":context()})

def test_context_cannot_claim_king_as_donor(profiles):
    with pytest.raises(ValueError,match="distinct fielded"):
        assess_army_goblin_projectile(
            army=army(profiles),
            contexts_by_king_id={"king-1":context(friendly_model_id="king-1")})

def test_no_foreign_context(profiles):
    with pytest.raises(ValueError,match="unknown/non-King"):
        assess_army_goblin_projectile(
            army=army(profiles,with_king=False),contexts_by_king_id={
                "king-1":context()})

def test_wrong_donor_race_rejected(profiles):
    a=SimpleNamespace(fielded_models=lambda:(
        SimpleNamespace(id="king-1",configured_profile=profiles["GT_KING"]),
        SimpleNamespace(id="ogre-1",configured_profile=profiles["GUNDABAD_OGRE"]),
    ))
    with pytest.raises(ValueError,match="not a Goblin"):
        assess_army_goblin_projectile(
            army=a,contexts_by_king_id={
                "king-1":context(friendly_model_id="ogre-1")})

def test_conflicting_donor_context_rejected(profiles):
    with pytest.raises(ValueError,match="contradicts"):
        assess_army_goblin_projectile(
            army=army(profiles),contexts_by_king_id={
                "king-1":context(friendly_is_goblin=False)})

def test_does_not_mutate_army(profiles):
    a=army(profiles)
    original=a.fielded_models()
    assess_army_goblin_projectile(
        army=a,contexts_by_king_id={"king-1":context()})
    assert a.fielded_models()==original

def test_mapping_required(profiles):
    with pytest.raises(TypeError,match="mapping"):
        assess_army_goblin_projectile(
            army=army(profiles),contexts_by_king_id=None)
