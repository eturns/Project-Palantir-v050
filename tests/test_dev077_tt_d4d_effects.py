"""DEV-077-TT-D4D purchased rules; pure standalone contract tests."""
import pytest
from three_trolls_hoard import HoardEvidence
from three_trolls_d4d_effects import (
    validate_livestock_placement, consume_livestock, cover_of_darkness,
    place_stash, stash_objective_presence, enemy_remove_stash,
)


def hoard(*names):
    return HoardEvidence("THREE_TROLLS", names, 50 * len(names), (), 6.0)


LIVESTOCK = hoard("Tasty Livestock")
DARKNESS = hoard("Cover of Darkness")
STASH = hoard("\"That's Mine That Is!\"")


def placement(h=LIVESTOCK, **kw):
    params = dict(proposed_position=(12, 12), board_width_inches=48,
                  board_height_inches=48, after_both_deployed=True,
                  before_first_turn=True)
    params.update(kw)
    return validate_livestock_placement(h, **params)


@pytest.mark.parametrize("pos", [(6,6), (6,42), (42,6), (42,42), (24,24)])
def test_livestock_legal_boundaries(pos):
    assert placement(proposed_position=pos).allowed


@pytest.mark.parametrize("pos", [(5.99,12), (12,5.99), (42.01,12), (-1,12)])
def test_livestock_edge_exclusion(pos):
    assert not placement(proposed_position=pos).allowed


@pytest.mark.parametrize("key,loc", [
    ("enemy_positions", (14.99,12)),
    ("objective_positions", (12,14.99)),
    ("existing_livestock_positions", (17.99,12)),
])
def test_livestock_near_other_entities(key,loc):
    assert not placement(**{key:[loc]}).allowed


@pytest.mark.parametrize("key,loc", [
    ("enemy_positions", (15,12)),
    ("objective_positions", (12,15)),
    ("existing_livestock_positions", (18,12)),
])
def test_livestock_exactly_exclusion_is_legal(key,loc):
    assert placement(**{key:[loc]}).allowed


def test_livestock_max_four():
    assert not placement(existing_livestock_positions=[(20,20)] * 4).allowed


@pytest.mark.parametrize("after,before", [(False,True),(True,False),(False,False)])
def test_livestock_timing(after,before):
    assert not placement(after_both_deployed=after, before_first_turn=before).allowed


def test_unpurchased_livestock():
    assert placement(hoard()).reason == "not_purchased"


@pytest.mark.parametrize("model", ["TT_BILL", "TT_BERT", "TT_TOM"])
def test_livestock_heals_one_lost_wound(model):
    r = consume_livestock(LIVESTOCK, model, distance_inches=3,
        during_own_activation=True, friendly_marker_present=True, wounds_lost=3)
    assert r.eligible and r.marker_removed and r.wounds_restored == 1


def test_livestock_no_overheal():
    r = consume_livestock(LIVESTOCK, "TT_BILL", distance_inches=0,
        during_own_activation=True, friendly_marker_present=True, wounds_lost=0)
    assert r.marker_removed and r.wounds_restored == 0


@pytest.mark.parametrize("modification", [
    {"distance_inches":3.01}, {"during_own_activation":False},
    {"friendly_marker_present":False},
])
def test_livestock_cannot_consume(modification):
    kwargs = dict(distance_inches=3, during_own_activation=True,
                  friendly_marker_present=True, wounds_lost=2)
    kwargs.update(modification)
    r = consume_livestock(LIVESTOCK, "TT_BERT", **kwargs)
    assert not r.eligible and not r.marker_removed


def test_livestock_purchase_required():
    r=consume_livestock(hoard(), "TT_BILL", distance_inches=1,
      during_own_activation=True,friendly_marker_present=True,wounds_lost=2)
    assert not r.eligible


@pytest.mark.parametrize("model", ["TT_BILL","TT_BERT","TT_TOM"])
def test_darkness_grants_cave_dweller(model):
    r=cover_of_darkness(DARKNESS,model,at_start_of_game=True,select_night=True)
    assert r.grants_cave_dweller and r.night_selected and r.status=="evaluated"


def test_darkness_optional_daylight():
    r=cover_of_darkness(DARKNESS,"TT_TOM",at_start_of_game=True,select_night=False)
    assert r.grants_cave_dweller and not r.night_selected


def test_darkness_not_purchased():
    r=cover_of_darkness(hoard(),"TT_BILL")
    assert not r.grants_cave_dweller and not r.may_choose_night


def test_darkness_refuses_late_night():
    with pytest.raises(ValueError):
        cover_of_darkness(DARKNESS,"TT_BILL",at_start_of_game=False,select_night=True)


def test_darkness_unknown_choice():
    assert cover_of_darkness(DARKNESS,"TT_BILL").status=="conditional_not_evaluated"


@pytest.mark.parametrize("model", ["TT_BILL","TT_BERT","TT_TOM"])
def test_stash_legal_placement(model):
    r=place_stash(STASH,model,at_start_of_activation=True,
        troll_has_stash=False,placed_in_base_contact=True)
    assert r.allowed and r.marker_base_mm==25


@pytest.mark.parametrize("changes", [
    {"at_start_of_activation":False},
    {"troll_has_stash":True},
    {"placed_in_base_contact":False},
])
def test_stash_illegal_placement(changes):
    kw=dict(at_start_of_activation=True,troll_has_stash=False,
            placed_in_base_contact=True)
    kw.update(changes)
    assert not place_stash(STASH,"TT_BILL",**kw).allowed


def test_stash_purchase_required():
    assert not place_stash(hoard(),"TT_BILL",
      at_start_of_activation=True,troll_has_stash=False,
      placed_in_base_contact=True).allowed


@pytest.mark.parametrize("exists,range_,count", [
    (True,True,1),(True,False,0),(False,True,0),
])
def test_stash_objective_count(exists,range_,count):
    r=stash_objective_presence(STASH,marker_exists=exists,within_objective_range=range_)
    assert r.friendly_warrior_equivalent==count


def test_stash_unknown_range_is_not_scored():
    r=stash_objective_presence(STASH,marker_exists=True,within_objective_range=None)
    assert r.status=="conditional_not_evaluated" and r.friendly_warrior_equivalent==0


def test_stash_unpurchased_cannot_count():
    assert stash_objective_presence(hoard(),marker_exists=True,
       within_objective_range=True).friendly_warrior_equivalent==0


def removal(h=STASH, **updates):
    kw=dict(marker_exists=True,enemy_in_base_contact=True,during_end_phase=True)
    kw.update(updates)
    return enemy_remove_stash(h,**kw)


def test_stash_valid_end_phase_removal():
    assert removal().enemy_can_remove


@pytest.mark.parametrize("flag", [
    "cast_magic", "used_missile_weapon", "engaged_in_combat",
    "supported_combat", "unable_to_move", "under_enemy_magic",
])
def test_stash_six_disqualifiers(flag):
    result=removal(**{flag:True})
    assert not result.enemy_can_remove and result.reason=="disqualified_by_turn_activity"


@pytest.mark.parametrize("change", [
    {"marker_exists":False}, {"enemy_in_base_contact":False},
    {"during_end_phase":False},
])
def test_stash_removal_requires_conditions(change):
    assert not removal(**change).enemy_can_remove


def test_unpurchased_stash_cannot_be_removed():
    assert not removal(hoard()).enemy_can_remove


@pytest.mark.parametrize("model", ["MORDOR_ORC", "TT_OTHER"])
def test_only_three_trolls_can_use_model_specific_effects(model):
    with pytest.raises(ValueError):
        consume_livestock(LIVESTOCK,model,distance_inches=1,
            during_own_activation=True,friendly_marker_present=True,wounds_lost=1)
    with pytest.raises(ValueError):
        cover_of_darkness(DARKNESS,model)
    with pytest.raises(ValueError):
        place_stash(STASH,model,at_start_of_activation=True,
          troll_has_stash=False,placed_in_base_contact=True)
