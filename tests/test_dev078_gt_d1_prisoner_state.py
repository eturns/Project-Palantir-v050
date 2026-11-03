"""DEV-078-GT-D1 — capture state acceptance.

Author: Edward Turns (Project Lead)
All facts explicit; no point award or battlefield-state inference.
"""
from dataclasses import replace
import pytest
from goblin_town_prisoner_state import (
    RULE_ID, Prisoner, PrisonerState, PrisonerChoice,
    PrisonerCaptureEvent, resolve_prisoner_capture, prisoner_for,
)


def event(**changes):
    data=dict(
        army_list_id="GOBLIN_TOWN",active_army_rule_ids=(RULE_ID,),
        captor_model_id="king-1",captor_profile_id="GT_KING",
        victim_model_id="enemy-hero-1",victim_is_enemy=True,
        victim_is_hero=True,victim_is_monster=False,killed_in_combat=True,
        choice=PrisonerChoice.TAKE_NEW,
    )
    data.update(changes)
    return PrisonerCaptureEvent(**data)


def resolve(state=None, **changes):
    return resolve_prisoner_capture(state if state is not None else PrisonerState(),event(**changes))


@pytest.mark.parametrize("captor",["GT_KING","GT_GRINNAH"])
def test_eligible_captors_capture(captor):
    result=resolve(captor_profile_id=captor)
    assert result.eligible and result.captured
    assert prisoner_for(result.state,"king-1")=="enemy-hero-1"
    assert result.state.casualty_ids==("enemy-hero-1",)


@pytest.mark.parametrize("changes",[
    {"army_list_id":"GUNDABAD"},
    {"active_army_rule_ids":()},
    {"captor_profile_id":"GT_CAPTAIN"},
    {"captor_profile_id":"GT_SCRIBE"},
    {"captor_profile_id":"GT_GOLLUM"},
    {"victim_is_hero":False},
    {"victim_is_monster":True},
])
def test_ineligible_combat_kills_are_casualties_but_not_prisoners(changes):
    result=resolve(**changes)
    assert not result.eligible and not result.captured
    assert result.state.prisoners==()
    assert result.state.casualty_ids==("enemy-hero-1",)


def test_non_enemy_not_captured_or_marked_enemy_casualty():
    result=resolve(victim_is_enemy=False)
    assert result.state==PrisonerState()
    assert result.status=="not_enemy"


def test_no_combat_kill_does_not_consume_victim():
    result=resolve(killed_in_combat=False)
    assert result.state==PrisonerState()
    assert not result.captured


def test_decline_still_records_combat_casualty():
    result=resolve(choice=PrisonerChoice.DECLINE)
    assert result.eligible and not result.captured
    assert result.state.casualty_ids==("enemy-hero-1",)
    assert result.status=="declined"


def test_two_captors_have_independent_slots():
    a=resolve()
    b=resolve(a.state,captor_model_id="grinnah-1",captor_profile_id="GT_GRINNAH",
              victim_model_id="enemy-hero-2")
    assert len(b.state.prisoners)==2
    assert prisoner_for(b.state,"king-1")=="enemy-hero-1"
    assert prisoner_for(b.state,"grinnah-1")=="enemy-hero-2"


def test_replacement_does_not_restore_old_prisoner():
    a=resolve()
    b=resolve(a.state,victim_model_id="enemy-hero-2")
    assert b.status=="replaced"
    assert b.replaced_victim_model_id=="enemy-hero-1"
    assert prisoner_for(b.state,"king-1")=="enemy-hero-2"
    assert b.state.casualty_ids==("enemy-hero-1","enemy-hero-2")


def test_replacement_preserves_other_captor():
    a=resolve()
    b=resolve(a.state,captor_model_id="grinnah-1",captor_profile_id="GT_GRINNAH",
              victim_model_id="enemy-hero-2")
    c=resolve(b.state,victim_model_id="enemy-hero-3")
    assert prisoner_for(c.state,"grinnah-1")=="enemy-hero-2"
    assert prisoner_for(c.state,"king-1")=="enemy-hero-3"


def test_keep_existing_marks_new_victim_as_casualty():
    a=resolve()
    b=resolve(a.state,victim_model_id="enemy-hero-2",choice=PrisonerChoice.KEEP_EXISTING)
    assert b.status=="kept_existing"
    assert prisoner_for(b.state,"king-1")=="enemy-hero-1"
    assert b.state.casualty_ids==("enemy-hero-1","enemy-hero-2")


def test_cannot_keep_missing_prisoner():
    with pytest.raises(ValueError,match="No existing prisoner"):
        resolve(choice=PrisonerChoice.KEEP_EXISTING)


def test_cannot_resolve_same_victim_twice():
    first=resolve()
    with pytest.raises(ValueError,match="already"):
        resolve(first.state)


@pytest.mark.parametrize("bad",[
    True,False,1,None,"TAKE_NEW",
])
def test_bad_choice_rejected(bad):
    with pytest.raises(TypeError):
        event(choice=bad)


@pytest.mark.parametrize("field",[
    "victim_is_enemy","victim_is_hero","victim_is_monster","killed_in_combat",
])
def test_boolean_validation(field):
    with pytest.raises(TypeError):
        event(**{field:1})


def test_invalid_prisoner_state_duplicate_slot():
    with pytest.raises(ValueError,match="Duplicate"):
        PrisonerState(
            (Prisoner("a","king"),Prisoner("b","king")),
            ("a","b"),
        )


def test_invalid_prisoner_state_requires_casualty():
    with pytest.raises(ValueError,match="casualties"):
        PrisonerState((Prisoner("a","king"),),())


def test_repeated_casualty_rejected():
    with pytest.raises(ValueError,match="Duplicate"):
        PrisonerState(casualty_ids=("a","a"))


def test_inactive_rule_has_no_capture():
    assert not resolve(active_army_rule_ids=()).captured


def test_immutable_state_after_update():
    old=PrisonerState()
    first=resolve(old)
    assert old==PrisonerState()
    assert first.state!=old


def test_result_state_is_deterministic():
    assert resolve()==resolve()


def test_non_prisoner_query():
    assert prisoner_for(PrisonerState(),"grinnah-1") is None


def test_capture_outcome_confirms_enemy_casualty():
    result=resolve()
    assert result.killed_enemy_recorded
