"""DEV-078-GT-D2: prisoner Victory Point acceptance.

Author: Edward Turns (Project Lead).
"""
from dataclasses import replace
import pytest

from goblin_town_prisoner_state import (
    RULE_ID, Prisoner, PrisonerState, PrisonerChoice,
    PrisonerCaptureEvent, resolve_prisoner_capture,
)
from goblin_town_prisoner_victory_points import (
    MAX_ARMY_VP, CaptorEndgameStatus, PrisonerVictoryPointRequest,
    calculate_prisoner_victory_points,
)


KING = CaptorEndgameStatus("king-1", "GT_KING", True)
GRINNAH = CaptorEndgameStatus("grinnah-1", "GT_GRINNAH", True)


def ledger(*captives):
    prisoners = tuple(Prisoner(victim, captor) for victim, captor in captives)
    return PrisonerState(prisoners, tuple(victim for victim, _ in captives))


def request(**changes):
    data = dict(army_list_id="GOBLIN_TOWN",
                active_army_rule_ids=(RULE_ID,),
                scenario_victory_points=0,
                captors=(KING, GRINNAH))
    data.update(changes)
    return PrisonerVictoryPointRequest(**data)


def score(state=None, **changes):
    return calculate_prisoner_victory_points(
        state if state is not None else ledger(("hero-1", "king-1")),
        request(**changes),
    )


def test_one_king_prisoner_one_point():
    s = score()
    assert (s.eligible_prisoner_victory_points,
            s.awarded_prisoner_victory_points, s.final_victory_points) == (1, 1, 1)


def test_grinnah_prisoner_one_point():
    s = score(ledger(("hero-2", "grinnah-1")))
    assert s.final_victory_points == 1


def test_both_captors_alive_two_points():
    s = score(ledger(("hero-1", "king-1"), ("hero-2", "grinnah-1")))
    assert s.eligible_prisoner_victory_points == 2
    assert s.awarded_prisoner_victory_points == 2
    assert len(s.lines) == 2


@pytest.mark.parametrize("dead", ["king", "grinnah"])
def test_dead_captor_scores_nothing(dead):
    statuses = (
        replace(KING, alive_at_end=dead != "king"),
        replace(GRINNAH, alive_at_end=dead != "grinnah"),
    )
    s = score(ledger(("hero-1", "king-1"), ("hero-2", "grinnah-1")),
              captors=statuses)
    assert s.awarded_prisoner_victory_points == 1


def test_both_dead_no_vp():
    s=score(ledger(("hero-1", "king-1"), ("hero-2", "grinnah-1")),
            captors=(replace(KING,alive_at_end=False),
                     replace(GRINNAH,alive_at_end=False)))
    assert s.awarded_prisoner_victory_points == 0


@pytest.mark.parametrize("base, expected_awarded, expected_final", [
    (0, 2, 2), (10, 2, 12), (18, 2, 20),
    (19, 1, 20), (20, 0, 20),
])
def test_twenty_point_ceiling(base, expected_awarded, expected_final):
    s = score(ledger(("hero-1","king-1"),("hero-2","grinnah-1")),
              scenario_victory_points=base)
    assert s.awarded_prisoner_victory_points == expected_awarded
    assert s.final_victory_points == expected_final
    assert s.capped is (expected_awarded < 2)
    assert sum(line.awarded_vp for line in s.lines) == expected_awarded


def test_no_prisoners_no_bonus():
    s=score(PrisonerState(),scenario_victory_points=11)
    assert s.final_victory_points == 11
    assert s.awarded_prisoner_victory_points == 0


def test_unheld_casualty_no_vp():
    s=score(PrisonerState(casualty_ids=("dead-hero",)))
    assert s.final_victory_points == 0


def test_replaced_prisoner_not_double_counted():
    first=PrisonerState((Prisoner("hero-1","king-1"),),("hero-1",))
    event=PrisonerCaptureEvent(
        army_list_id="GOBLIN_TOWN",active_army_rule_ids=(RULE_ID,),
        captor_model_id="king-1",captor_profile_id="GT_KING",
        victim_model_id="hero-2",victim_is_enemy=True,victim_is_hero=True,
        victim_is_monster=False,killed_in_combat=True,choice=PrisonerChoice.TAKE_NEW,
    )
    second=resolve_prisoner_capture(first,event)
    assert second.replaced_victim_model_id=="hero-1"
    assert second.state.casualty_ids==("hero-1","hero-2")
    assert score(second.state).awarded_prisoner_victory_points == 1


def test_keep_existing_prisoner_not_double_counted():
    state=PrisonerState(
        (Prisoner("hero-1","king-1"),),("hero-1","hero-2"))
    assert score(state).awarded_prisoner_victory_points == 1


def test_score_does_not_mutate_prisoner_state():
    state=ledger(("hero-1","king-1"))
    before=repr(state)
    score(state)
    assert repr(state)==before


def test_deterministic_results():
    state=ledger(("hero-1","king-1"),("hero-2","grinnah-1"))
    assert score(state)==score(state)


def test_no_score_injection():
    s=score()
    assert s.dashboard_score is None and s.scenario_score is None


def test_requires_survival_data_for_held_prisoner():
    with pytest.raises(ValueError, match="Missing captor"):
        score(captors=(GRINNAH,))


def test_dead_captor_represented_explicitly_not_omitted():
    result=score(captors=(replace(KING,alive_at_end=False), GRINNAH))
    assert result.lines[0].captor_alive is False
    assert result.awarded_prisoner_victory_points == 0


def test_missing_army_rule_rejects_nonempty_ledger():
    with pytest.raises(ValueError,match="entitled"):
        score(active_army_rule_ids=())


def test_wrong_army_rejects_nonempty_ledger():
    with pytest.raises(ValueError,match="entitled"):
        score(army_list_id="GUNDABAD")


def test_empty_ledger_without_rule_leaves_scenario_points():
    result=score(PrisonerState(),active_army_rule_ids=(),
                 scenario_victory_points=13)
    assert result.final_victory_points==13


@pytest.mark.parametrize("base",[-1,21,True,1.5,"11",None])
def test_invalid_scenario_points(base):
    with pytest.raises(ValueError,match="Scenario VP"):
        request(scenario_victory_points=base)


def test_duplicate_captor_model_rejected():
    with pytest.raises(ValueError,match="Duplicate captor model"):
        score(captors=(KING,KING))


def test_duplicate_unique_profile_rejected():
    with pytest.raises(ValueError,match="Duplicate unique"):
        score(captors=(KING, CaptorEndgameStatus("king-2","GT_KING",True)))


def test_non_eligible_captor_profile_rejected():
    with pytest.raises(ValueError,match="Only the Goblin King"):
        score(captors=(KING, CaptorEndgameStatus("captain","GT_CAPTAIN",True)))


@pytest.mark.parametrize("bad",[0,1,"yes",None])
def test_invalid_survival_flag_rejected(bad):
    with pytest.raises(TypeError,match="survival"):
        CaptorEndgameStatus("king-1","GT_KING",bad)


def test_prisoner_state_type_rejected():
    with pytest.raises(TypeError,match="PrisonerState"):
        calculate_prisoner_victory_points(None,request())


def test_request_type_rejected():
    with pytest.raises(TypeError,match="PrisonerVictoryPointRequest"):
        calculate_prisoner_victory_points(PrisonerState(),None)


def test_duplicate_prisoner_captor_state_rejected():
    with pytest.raises(ValueError,match="Duplicate captor"):
        ledger(("hero-1","king-1"),("hero-2","king-1"))


def test_reordered_captor_evidence_same_score():
    state=ledger(("hero-1","king-1"),("hero-2","grinnah-1"))
    first=score(state)
    second=score(state,captors=(GRINNAH,KING))
    assert first==second


def test_boundary_cap_20_constant():
    assert MAX_ARMY_VP == 20
