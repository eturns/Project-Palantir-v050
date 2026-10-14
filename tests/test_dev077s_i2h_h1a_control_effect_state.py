"""Focused regression for verified and explicitly conditional Control states."""
from dataclasses import replace
from fractions import Fraction

import pytest

from control_effect_state import (
    ControlExpiry, ControlState, apply_confirmed_control_effect,
    expire_control_effects, restrictions_for_target,
)
from hero_hunting_control_spells import (
    calculate_compel_hero_hunting, calculate_transfix_hero_hunting,
)


def transfix():
    return calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2))


def compel(*, engaged=False):
    return calculate_compel_hero_hunting(
        effect_probability=Fraction(1, 3), target_move_inches=5,
        target_engaged_in_combat=engaged,
    )


def apply(state=None, *, evidence=None, effect_id="one", target_id="enemy"):
    return apply_confirmed_control_effect(
        ControlState() if state is None else state,
        effect_id=effect_id, source_id="caster", target_id=target_id,
        evidence=transfix() if evidence is None else evidence,
        cast_and_resist_resolved=True, target_legality_verified=True,
    )


def test_initial_state_is_empty_and_no_score_fields():
    state = ControlState()
    assert state.active_effects == ()
    assert not restrictions_for_target(state, target_id="enemy").activation_blocked
    assert not hasattr(state, "dashboard_score")


def test_transfix_restrictions_and_expiry():
    state = apply()
    r = restrictions_for_target(state, target_id="enemy")
    assert r.activation_blocked and r.shooting_blocked and r.heroic_actions_blocked
    assert r.active_abilities_blocked and r.strikes_when_winning_duel_blocked
    assert r.contributing_effect_ids == ("one",)
    assert not restrictions_for_target(state, target_id="other").activation_blocked
    assert expire_control_effects(state, boundary=ControlExpiry.END_PHASE) == ControlState()


def test_compel_fractional_movement_and_turn_expiry():
    state = apply(evidence=compel())
    r = restrictions_for_target(state, target_id="enemy")
    assert r.compelled_max_movement_inches == Fraction(5, 2)
    assert r.further_movement_blocked
    assert not r.activation_blocked and not r.shooting_blocked
    assert expire_control_effects(state, boundary=ControlExpiry.END_PHASE) == state
    assert expire_control_effects(state, boundary=ControlExpiry.TURN_END) == ControlState()


def test_engaged_compel_retains_existing_rule_evidence():
    state = apply(evidence=compel(engaged=True))
    assert restrictions_for_target(state, target_id="enemy").compelled_max_movement_inches == 0
    assert state.active_effects[0].evidence_status == "engaged_target_cannot_be_moved_out_of_combat"


def test_overlapping_effects_are_aggregated_without_independent_scores():
    state = apply()
    state = apply(state, evidence=compel(), effect_id="two")
    r = restrictions_for_target(state, target_id="enemy")
    assert r.activation_blocked and r.further_movement_blocked
    assert r.contributing_effect_ids == ("one", "two")
    state = expire_control_effects(state, boundary=ControlExpiry.END_PHASE)
    assert not restrictions_for_target(state, target_id="enemy").activation_blocked
    assert restrictions_for_target(state, target_id="enemy").further_movement_blocked


@pytest.mark.parametrize("cast_ok,legal_ok", [(False, True), (True, False), (False, False)])
def test_unverified_effects_fail_closed(cast_ok, legal_ok):
    with pytest.raises(ValueError, match="verified success and legality"):
        apply_confirmed_control_effect(
            ControlState(), effect_id="one", source_id="caster", target_id="enemy",
            evidence=transfix(), cast_and_resist_resolved=cast_ok,
            target_legality_verified=legal_ok,
        )


def test_duplicate_effect_id_rejected():
    with pytest.raises(ValueError, match="already exists"):
        apply(apply())


def test_unknown_duration_and_effect_rejected():
    with pytest.raises(ValueError, match="unsupported spell or effect duration"):
        apply(evidence=replace(transfix(), duration="permanent"))
    with pytest.raises(ValueError, match="unsupported spell or effect duration"):
        apply(evidence=replace(transfix(), spell_id="UNKNOWN"))


def test_unverified_evidence_status_rejected():
    with pytest.raises(ValueError, match="unsupported evidence status"):
        apply(evidence=replace(transfix(), evidence_status="speculative"))


def test_original_state_is_immutable():
    original = ControlState()
    updated = apply(original)
    assert not original.active_effects
    assert len(updated.active_effects) == 1


def test_invalid_inputs_fail_closed():
    with pytest.raises(TypeError, match="boundary"):
        expire_control_effects(ControlState(), boundary="end_phase")
    with pytest.raises(ValueError, match="target_id"):
        restrictions_for_target(ControlState(), target_id=" ")
    with pytest.raises(TypeError, match="resolution"):
        apply_confirmed_control_effect(
            ControlState(), effect_id="one", source_id="caster", target_id="enemy",
            evidence=transfix(), cast_and_resist_resolved=1, target_legality_verified=True,
        )
