"""DEV-078-GT-B3: imported real-army song integration.

Author: Edward Turns (Project Lead).
"""
from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import pytest

from tests.test_dev077_gt_d1_import_integrity import production as gt_production
from army_loader import load_army_rules
from analysis_loader import load_metric_thresholds
from goblin_town_songs import Song, SongState, end_phase, next_turn
from goblin_town_songs_service import SongArmyRequest, build_goblin_town_song_army_evidence
from services.army_analysis_service import analyse_imported_army


@pytest.fixture(scope="module")
def production(gt_production):
    _, lists, imported = gt_production
    load_army_rules(lists)
    definition,army,army_list=imported
    army_list.army_rules=lists["GOBLIN_TOWN"].army_rules
    return definition,army,army_list


def requested(production,song=Song.BATTER_AND_BEAT,**overrides):
    _,army,_=production
    models=tuple(m for m in army.fielded_models() if m.configured_profile is not None)
    ids=tuple((m.id, 6.0) for m in models)
    d=dict(state=SongState(),king_alive=True,king_on_battlefield=True,
           priority_determined=True,selected_song=song,friendly_model_distances=ids)
    d.update(overrides)
    return SongArmyRequest(**d)


def assess(production,request=None):
    d,a,l=production
    return build_goblin_town_song_army_evidence(a,l,army_definition=d,
                                              request=request or requested(production))


def test_registered_rule(production):
    assert any(x.id=="GT_I_FEEL_A_SONG_COMING_ON" for x in production[2].army_rules)


def test_general_is_imported_king(production):
    result=assess(production)
    king=next(x for x in production[1].fielded_models() if x.id==result.king_model_id)
    assert king.profile_id=="GT_KING"


@pytest.mark.parametrize("song",list(Song))
def test_every_song_can_be_declared(production,song):
    ev=assess(production,requested(production,song))
    assert ev.command.sung and ev.command.state.active_song==song


def test_banner_excludes_king_and_gollum(production):
    ev=assess(production)
    assert any(x.banner_support for x in ev.model_effects)
    assert all(not x.banner_support for x in ev.model_effects if x.profile_id in ("GT_KING","GT_GOLLUM"))


def test_terror_excludes_king(production):
    ev=assess(production,requested(production,Song.YAMMER_AND_YELP))
    assert any(x.causes_terror for x in ev.model_effects)
    assert all(not x.causes_terror for x in ev.model_effects if x.profile_id=="GT_KING")


def test_prevention_is_one_sixth(production):
    ev=assess(production,requested(production,Song.ABOMINATIONS))
    assert any(x.wound_prevention_probability==Fraction(1,6) for x in ev.model_effects)
    assert all(x.wound_prevention_probability==0 for x in ev.model_effects if x.profile_id=="GT_KING")


def test_reroll_natural_one_for_strikes(production):
    ev=assess(production,requested(production,Song.BONES_WILL_BE_SHATTERED))
    assert any(x.reroll_natural_ones_on_strikes for x in ev.model_effects)
    assert all(not x.reroll_natural_ones_on_strikes for x in ev.model_effects if x.profile_id=="GT_KING")


def test_distance_outside_six_excludes_every_target(production):
    r=requested(production)
    farther=replace(r,friendly_model_distances=tuple((i,6.01) for i,_ in r.friendly_model_distances))
    ev=assess(production,farther)
    assert not any(x.banner_support for x in ev.model_effects)


def test_unknown_model_rejected(production):
    with pytest.raises(ValueError,match="not fielded"):
        assess(production,requested(production,friendly_model_distances=(("unknown",3.0),)))


def test_bad_distance_rejected(production):
    model_id=requested(production).friendly_model_distances[0][0]
    with pytest.raises(ValueError,match="Distance"):
        assess(production,requested(production,friendly_model_distances=((model_id,-1),)))


def test_duplicate_model_rejected(production):
    model_id=requested(production).friendly_model_distances[0][0]
    with pytest.raises(ValueError,match="Duplicate"):
        assess(production,requested(production,friendly_model_distances=((model_id,3),(model_id,4))))


def test_missing_rule_rejected(production):
    d,a,l=production
    with pytest.raises(ValueError,match="not registered"):
        build_goblin_town_song_army_evidence(a,SimpleNamespace(id=l.id,army_rules=[]),
            army_definition=d,request=requested(production))


def test_wrong_army_rejected(production):
    d,a,l=production
    with pytest.raises(ValueError,match="Goblin-town"):
        build_goblin_town_song_army_evidence(a,SimpleNamespace(id="GUNDABAD",army_rules=l.army_rules),
            army_definition=d,request=requested(production))


def test_next_turn_same_song_rejected(production):
    first=assess(production)
    state=next_turn(end_phase(first.command.state))
    second=assess(production,requested(production,state=state))
    assert not second.command.sung and second.command.status=="same_song_as_previous_turn"


def test_next_turn_different_song_allowed(production):
    first=assess(production)
    state=next_turn(end_phase(first.command.state))
    second=assess(production,requested(production,Song.ABOMINATIONS,state=state))
    assert second.command.sung


@pytest.mark.parametrize("field",["king_alive","king_on_battlefield","priority_determined"])
def test_king_or_timing_unavailable(production,field):
    outcome=assess(production,requested(production,**{field:False}))
    assert not outcome.command.sung


def test_service_diagnostic_and_score_preservation(production):
    d,a,l=production
    baseline=analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds())
    with_song=analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds(),
        goblin_town_army_definition=d,goblin_town_song_request=requested(production))
    assert with_song["mechanical_goblin_town_songs"].command.sung
    for key in ("metric_densities","metric_assessments","battlefield_assessments"):
        assert baseline[key]==with_song[key]
    assert "mechanical_goblin_town_songs" not in baseline


def test_service_requires_definition(production):
    _,a,l=production
    with pytest.raises(ValueError,match="imported Goblin-town definition"):
        analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds(),
                             goblin_town_song_request=requested(production))
