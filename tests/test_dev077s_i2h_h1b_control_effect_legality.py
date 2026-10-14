"""DEV-077S-I2-H1-B: legality gate and conditional transition regression."""
from fractions import Fraction

import pytest

from control_effect_state import (
    ControlExpiry,
    ControlState,
    expire_control_effects,
)
from control_effect_legality import (
    ActionLegality,
    ControlAction,
    ControlOpportunity,
    EvidenceVerdict,
    evaluate_control_action,
    resolve_control_application,
)
from hero_hunting_control_spells import (
    calculate_compel_hero_hunting,
    calculate_transfix_hero_hunting,
)

YES = EvidenceVerdict.VERIFIED_TRUE
NO = EvidenceVerdict.VERIFIED_FALSE
UNKNOWN = EvidenceVerdict.UNKNOWN


def evidence(spell="TRANSFIX"):
    if spell == "TRANSFIX":
        return calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2))
    return calculate_compel_hero_hunting(effect_probability=Fraction(1, 3), target_move_inches=6)


def attempt(state=None, *, available=YES, legal=YES, succeeded=YES, spell="TRANSFIX", effect_id="effect"):
    return resolve_control_application(
        ControlState() if state is None else state,
        effect_id=effect_id, source_id="caster", target_id="enemy",
        evidence=evidence(spell),
        opportunity=ControlOpportunity(available, legal, succeeded),
    )


def test_verified_success_applies_exactly_one_effect():
    result = attempt()
    assert result.applied and result.reason == "confirmed_applied"
    assert len(result.state.active_effects) == 1
    assert result.state.active_effects[0].target_id == "enemy"


@pytest.mark.parametrize("field,reason", [
    ("available", "caster_unavailable"),
    ("legal", "illegal_target"),
    ("succeeded", "effect_failed"),
])
def test_verified_failure_never_creates_an_effect(field, reason):
    before = ControlState()
    result = attempt(before, **{field: NO})
    assert not result.applied and result.reason == reason
    assert result.state is before


@pytest.mark.parametrize("field", ["available", "legal", "succeeded"])
def test_unknown_evidence_fails_closed_without_claiming_failure(field):
    result = attempt(**{field: UNKNOWN})
    assert result.reason == "unresolved_evidence"
    assert not result.applied and result.state == ControlState()


def test_false_precondition_dominates_unknown_evidence():
    result = attempt(available=UNKNOWN, legal=NO)
    assert not result.applied and result.reason == "illegal_target"


def test_original_state_is_preserved_on_new_transition():
    before = attempt().state
    after = attempt(before, spell="COMPEL", effect_id="second").state
    assert len(before.active_effects) == 1
    assert len(after.active_effects) == 2


def test_transfix_blocks_activation_and_shooting_even_when_other_checks_pass():
    state = attempt().state
    for action in (ControlAction.ACTIVATE, ControlAction.SHOOT, ControlAction.HEROIC_ACTION,
                   ControlAction.ACTIVE_ABILITY, ControlAction.STRIKE_AFTER_WINNING_DUEL):
        assert evaluate_control_action(state, target_id="enemy", action=action, other_legality=YES) is ActionLegality.BLOCKED_BY_CONTROL


def test_compel_blocks_only_further_movement_in_model():
    state = attempt(spell="COMPEL").state
    assert evaluate_control_action(state, target_id="enemy", action=ControlAction.MOVE_FURTHER, other_legality=YES) is ActionLegality.BLOCKED_BY_CONTROL
    assert evaluate_control_action(state, target_id="enemy", action=ControlAction.SHOOT, other_legality=YES) is ActionLegality.PERMITTED_BY_CONTROL


def test_no_control_block_does_not_imply_permission_without_other_evidence():
    state = ControlState()
    assert evaluate_control_action(state, target_id="enemy", action=ControlAction.SHOOT) is ActionLegality.UNRESOLVED
    assert evaluate_control_action(state, target_id="enemy", action=ControlAction.SHOOT, other_legality=NO) is ActionLegality.UNRESOLVED
    assert evaluate_control_action(state, target_id="enemy", action=ControlAction.SHOOT, other_legality=YES) is ActionLegality.PERMITTED_BY_CONTROL


def test_expiry_restores_control_permission_but_not_other_game_permission():
    state = attempt().state
    expired = expire_control_effects(state, boundary=ControlExpiry.END_PHASE)
    assert evaluate_control_action(expired, target_id="enemy", action=ControlAction.ACTIVATE) is ActionLegality.UNRESOLVED
    assert evaluate_control_action(expired, target_id="enemy", action=ControlAction.ACTIVATE, other_legality=YES) is ActionLegality.PERMITTED_BY_CONTROL


def test_overlap_preserves_strongest_control_restriction():
    transfix = attempt().state
    both = attempt(transfix, spell="COMPEL", effect_id="compel").state
    assert evaluate_control_action(both, target_id="enemy", action=ControlAction.ACTIVATE, other_legality=YES) is ActionLegality.BLOCKED_BY_CONTROL
    assert evaluate_control_action(both, target_id="enemy", action=ControlAction.MOVE_FURTHER, other_legality=YES) is ActionLegality.BLOCKED_BY_CONTROL


def test_other_target_is_not_inadvertently_restricted():
    state = attempt().state
    assert evaluate_control_action(state, target_id="friend", action=ControlAction.ACTIVATE, other_legality=YES) is ActionLegality.PERMITTED_BY_CONTROL


@pytest.mark.parametrize("bad", [True, "yes", None])
def test_invalid_verdicts_rejected(bad):
    with pytest.raises(TypeError, match="verdicts"):
        ControlOpportunity(bad, YES, YES)


def test_duplicate_id_is_never_accepted_even_if_second_attempt_fails():
    with pytest.raises(ValueError, match="already exists"):
        attempt(attempt().state, succeeded=NO)


def test_unsupported_spell_does_not_bypass_original_validation():
    from dataclasses import replace
    with pytest.raises(ValueError, match="unsupported spell"):
        resolve_control_application(
            ControlState(), effect_id="x", source_id="a", target_id="b",
            evidence=replace(evidence(), spell_id="UNKNOWN"),
            opportunity=ControlOpportunity(YES, YES, YES),
        )


def test_diagnostic_has_no_dashboard_or_scenario_score():
    result = attempt()
    assert not hasattr(result, "dashboard_score")
    assert not hasattr(result, "scenario_score")
