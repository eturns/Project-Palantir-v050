from types import SimpleNamespace
import pytest
from goblin_scribe_command import (
    WithMeContext, MightTransferContext, assess_with_me_extension, assess_might_transfer
)
def model(id):
    return SimpleNamespace(profile=SimpleNamespace(id=id))
KING=model("GT_KING")
SCRIBE=model("GT_SCRIBE")
def withme(**kwargs):
    a=dict(distance_king_to_scribe_inches=6,
           king_declared_heroic_move=True, king_called_with_me=True)
    a.update(kwargs)
    return WithMeContext(**a)
def transfer(**kwargs):
    a=dict(hero_is_friendly_goblin=True,hero_is_hero=True,
           hero_started_activation_within_scribe_inches=3,
           hero_might_remaining=1,king_might_spent=1,
           used_this_turn=False,hero_chooses_to_spend_might=True)
    a.update(kwargs)
    return MightTransferContext(**a)

def test_with_me_all_friendly_and_no_end_radius():
    r=assess_with_me_extension(KING,SCRIBE,withme())
    assert r.battlefield_wide_friendly_models
    assert r.removes_king_end_distance_requirement
@pytest.mark.parametrize("change",[
    {"distance_king_to_scribe_inches":6.01},
    {"king_declared_heroic_move":False},
    {"king_called_with_me":False}
])
def test_with_me_gate(change):
    assert not assess_with_me_extension(KING,SCRIBE,withme(**change)).battlefield_wide_friendly_models
def test_with_me_wrong_actor():
    assert not assess_with_me_extension(model("GT_CAPTAIN"),SCRIBE,withme()).battlefield_wide_friendly_models
def test_with_me_wrong_scribe():
    assert not assess_with_me_extension(KING,model("GT_WARRIOR"),withme()).battlefield_wide_friendly_models

def test_might_transfer_once_per_turn():
    r=assess_might_transfer(KING,SCRIBE,transfer())
    assert (r.eligible,r.hero_might_spent,r.king_might_recovered,r.consumes_once_per_turn_use)==(True,1,1,True)
@pytest.mark.parametrize("change",[
    {"hero_is_friendly_goblin":False},
    {"hero_is_hero":False},
    {"hero_started_activation_within_scribe_inches":3.01},
    {"hero_might_remaining":0},
    {"king_might_spent":0},
    {"used_this_turn":True},
    {"hero_chooses_to_spend_might":False}
])
def test_might_transfer_gate(change):
    r=assess_might_transfer(KING,SCRIBE,transfer(**change))
    assert not r.eligible
    assert r.hero_might_spent==0 and r.king_might_recovered==0
def test_might_wrong_actor():
    assert not assess_might_transfer(model("GT_GRINNAH"),SCRIBE,transfer()).eligible
def test_might_wrong_scribe():
    assert not assess_might_transfer(KING,model("GT_GRINNAH"),transfer()).eligible
@pytest.mark.parametrize("change",[
    {"hero_might_remaining":-1},
    {"king_might_spent":True},
    {"hero_started_activation_within_scribe_inches":float("nan")},
    {"used_this_turn":None}
])
def test_invalid_context_rejected(change):
    with pytest.raises((TypeError,ValueError)):
        transfer(**change)
def test_invalid_with_me_context():
    with pytest.raises(ValueError):
        withme(distance_king_to_scribe_inches=float("inf"))
