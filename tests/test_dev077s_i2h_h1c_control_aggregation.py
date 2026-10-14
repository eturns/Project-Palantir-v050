"""Focused DEV-077S-I2-H1-C tests: evidence-only aggregation."""
from dataclasses import replace
from fractions import Fraction

import pytest

from control_aggregation import ControlTurnObservation, aggregate_control_observations
from control_effect_legality import ControlAction, EvidenceVerdict
from control_effect_state import (
    ControlExpiry, ControlState, apply_confirmed_control_effect,
    expire_control_effects,
)
from hero_hunting_control_spells import (
    calculate_compel_hero_hunting, calculate_transfix_hero_hunting,
)


def state_with_transfix(target="orc", effect_id="t1"):
    return apply_confirmed_control_effect(
        ControlState(), effect_id=effect_id, source_id="necro", target_id=target,
        evidence=calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2)),
        cast_and_resist_resolved=True, target_legality_verified=True,
    )


def obs(state, action=ControlAction.ACTIVATE, *, turn=1, target="orc", verdict=EvidenceVerdict.VERIFIED_TRUE):
    return ControlTurnObservation(turn, target, action, state, verdict)


def test_confirmed_transfix_denies_one_observed_activation():
    result = aggregate_control_observations((obs(state_with_transfix()),))
    assert result.denied_action_count == 1
    assert result.affected_model_turn_count == 1
    assert result.denied_opportunities[0].contributing_effect_ids == ("t1",)


def test_unknown_opportunity_never_becomes_denial():
    result = aggregate_control_observations((obs(state_with_transfix(), verdict=EvidenceVerdict.UNKNOWN),))
    assert result.denied_action_count == 0
    assert len(result.unresolved_opportunities) == 1


def test_proven_absent_opportunity_is_not_denial():
    result = aggregate_control_observations((obs(state_with_transfix(), verdict=EvidenceVerdict.VERIFIED_FALSE),))
    assert result.affected_model_turn_count == 0
    assert len(result.verified_non_opportunities) == 1


def test_unblocked_opportunity_not_counted_as_denied():
    result = aggregate_control_observations((obs(ControlState()),))
    assert result.observed_action_opportunities == 1
    assert result.denied_action_count == 0


def test_multiple_denied_actions_same_model_turn_count_once():
    state = state_with_transfix()
    result = aggregate_control_observations((
        obs(state, ControlAction.ACTIVATE), obs(state, ControlAction.SHOOT),
    ))
    assert result.denied_action_count == 2
    assert result.affected_model_turn_count == 1


def test_duplicate_identical_observation_deduplicated():
    x = obs(state_with_transfix())
    result = aggregate_control_observations((x, x))
    assert result.denied_action_count == 1


def test_conflicting_duplicate_observation_rejected():
    a = obs(state_with_transfix())
    b = replace(a, opportunity=EvidenceVerdict.UNKNOWN)
    with pytest.raises(ValueError, match="conflicting evidence"):
        aggregate_control_observations((a, b))


def test_overlap_preserves_sources_without_double_counting():
    state = state_with_transfix()
    state = apply_confirmed_control_effect(
        state, effect_id="t2", source_id="other", target_id="orc",
        evidence=calculate_transfix_hero_hunting(effect_probability=Fraction(1, 3)),
        cast_and_resist_resolved=True, target_legality_verified=True,
    )
    result = aggregate_control_observations((obs(state),))
    assert result.denied_action_count == 1
    assert result.denied_opportunities[0].contributing_effect_ids == ("t1", "t2")


def test_end_phase_expiry_changes_later_observation():
    state = state_with_transfix()
    later = expire_control_effects(state, boundary=ControlExpiry.END_PHASE)
    result = aggregate_control_observations((obs(state), obs(later, turn=2)))
    assert result.denied_action_count == 1
    assert result.observed_action_opportunities == 2


def test_two_targets_and_turns_count_separately():
    a = state_with_transfix("orc")
    b = state_with_transfix("warg", "t2")
    result = aggregate_control_observations((obs(a), obs(b, target="warg"), obs(a, turn=2)))
    assert result.affected_model_turn_count == 3


def test_compel_further_movement_is_distinct_denial():
    state = apply_confirmed_control_effect(
        ControlState(), effect_id="c1", source_id="necro", target_id="orc",
        evidence=calculate_compel_hero_hunting(effect_probability=Fraction(1, 2), target_move_inches=6),
        cast_and_resist_resolved=True, target_legality_verified=True,
    )
    result = aggregate_control_observations((
        obs(state, ControlAction.MOVE_FURTHER), obs(state, ControlAction.SHOOT),
    ))
    assert result.denied_action_count == 1
    assert result.denied_opportunities[0].action is ControlAction.MOVE_FURTHER


def test_empty_observations_are_not_zero_capability_score():
    result = aggregate_control_observations(())
    assert result.denied_action_count == 0
    assert result.dashboard_score is None and result.scenario_score is None


def test_non_tuple_input_rejected():
    with pytest.raises(TypeError, match="tuple"):
        aggregate_control_observations([])


def test_invalid_turn_and_opportunity_rejected():
    with pytest.raises(ValueError, match="positive int"):
        obs(ControlState(), turn=0)
    with pytest.raises(TypeError, match="EvidenceVerdict"):
        obs(ControlState(), verdict=True)


def test_records_are_deterministically_ordered():
    state = state_with_transfix()
    result = aggregate_control_observations((obs(state, turn=3), obs(state, turn=1)))
    assert result.affected_model_turns == ((1, "orc"), (3, "orc"))
