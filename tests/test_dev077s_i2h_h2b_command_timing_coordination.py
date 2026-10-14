"""DEV-077S-I2-H2-B: timing uncertainty and shared Might tests."""
import pytest

from command_action_declaration import (
    CommandActionDeclaration, CommandCheck, CommandDecision,
)
from command_timing_coordination import (
    CommandTimingEntry, OrderEvidence, evaluate_command_timing,
)
from hero_resource_state import HeroResourceState

TRUE = CommandCheck.VERIFIED_TRUE
KNOWN = ("HEROIC_MOVE", "HEROIC_MARCH")


def entry(event, actor="A", *, key=None, seq=None, order=OrderEvidence.UNKNOWN,
          turn=1, might=1, action="HEROIC_MOVE", legal=TRUE):
    return CommandTimingEntry(
        CommandActionDeclaration(
            event_id=event, actor_id=actor, heroic_action_id=action,
            turn=turn, might_cost=might, timing_legal=legal,
            activation_legal=TRUE, battlefield_legal=TRUE,
        ),
        window_id="MOVE", conflict_key=key, sequence=seq, order_evidence=order,
    )


def run(entries, a=2, b=2):
    return evaluate_command_timing(
        entries,
        known_action_ids=KNOWN,
        available_actions_by_actor={"A": KNOWN, "B": KNOWN},
        starting_resources={
            "A": HeroResourceState(remaining_might=a),
            "B": HeroResourceState(remaining_might=b),
        },
    )


def test_uncontested_verified_declaration_spends_one_might():
    result = run((entry("e1"),))
    assert result.outcomes[0].decision is CommandDecision.PERMITTED
    assert result.total_might_spent == 1
    assert dict(result.remaining_resources)["A"].remaining_might == 1


def test_competing_actions_unknown_order_do_not_spend():
    result = run((entry("e1", key="contest"), entry("e2", "B", key="contest")))
    assert all(x.decision is CommandDecision.UNRESOLVED for x in result.outcomes)
    assert result.total_might_spent == 0


def test_partial_order_evidence_still_unresolved():
    result = run((entry("e1", key="c", seq=0, order=OrderEvidence.VERIFIED),
                  entry("e2", "B", key="c")))
    assert result.total_might_spent == 0


def test_verified_distinct_order_allows_both():
    result = run((entry("e1", key="c", seq=1, order=OrderEvidence.VERIFIED),
                  entry("e2", "B", key="c", seq=0, order=OrderEvidence.VERIFIED)))
    assert all(x.decision is CommandDecision.PERMITTED for x in result.outcomes)
    assert result.total_might_spent == 2


def test_equal_verified_sequence_is_collision_not_tie_break():
    result = run((entry("e1", key="c", seq=0, order=OrderEvidence.VERIFIED),
                  entry("e2", "B", key="c", seq=0, order=OrderEvidence.VERIFIED)))
    assert all(x.decision is CommandDecision.UNRESOLVED for x in result.outcomes)


def test_one_actor_cannot_spend_might_twice_from_one_point():
    result = run((entry("e1"), entry("e2")), a=1)
    assert [x.decision for x in result.outcomes] == [
        CommandDecision.PERMITTED, CommandDecision.FORBIDDEN
    ]
    assert result.total_might_spent == 1


def test_unresolved_opportunity_spends_nothing():
    result = run((entry("e1", legal=CommandCheck.UNKNOWN),))
    assert result.outcomes[0].decision is CommandDecision.UNRESOLVED
    assert result.total_might_spent == 0


def test_competing_group_does_not_block_unrelated_group():
    result = run((entry("e1", key="c"), entry("e2", "B", key="c"), entry("e3")))
    assert [o.decision for o in result.outcomes] == [
        CommandDecision.UNRESOLVED, CommandDecision.UNRESOLVED,
        CommandDecision.PERMITTED,
    ]


def test_same_key_in_different_turns_not_collision():
    result = run((entry("e1", key="c", turn=1), entry("e2", "B", key="c", turn=2)))
    assert result.total_might_spent == 2


def test_duplicate_event_rejected():
    with pytest.raises(ValueError, match="duplicate"):
        run((entry("same"), entry("same", "B")))


def test_unknown_actor_rejected():
    with pytest.raises(ValueError, match="unknown"):
        run((entry("e1", "C"),))


def test_verified_order_requires_sequence():
    with pytest.raises(ValueError, match="sequence"):
        entry("e1", order=OrderEvidence.VERIFIED)


def test_invalid_negative_sequence_rejected():
    with pytest.raises(ValueError, match="sequence"):
        entry("e1", seq=-1)


def test_no_effect_or_scores():
    result = run((entry("e1"),))
    assert result.dashboard_score is None and result.scenario_score is None
    assert not result.outcomes[0].effect_resolved


def test_invalid_availability_mismatch_rejected():
    with pytest.raises(ValueError, match="match"):
        evaluate_command_timing(
            (), known_action_ids=KNOWN,
            available_actions_by_actor={"A": KNOWN},
            starting_resources={},
        )
