"""DEV-078-AH-D1 — Morgul Arrows persistent battlefield-effect state.

Author: Edward Turns (Project Lead)

Standalone, explicit-event resolution. A qualifying unprevented Wound from
friendly shooting infects an enemy model. From the *following* turn's End
Phase, roll one D6 per affected model; a natural 1 causes an additional Wound.
Repeated qualifying hits never create multiple rolls. The caller is responsible
for applying additional Wounds and declaring removed models.
No dashboard or scenario scoring is performed.
"""
from dataclasses import dataclass
from fractions import Fraction

ARMY_LIST_ID = "AZOGS_HUNTERS"
RULE_ID = "DG_MORGUL_ARROWS"
END_PHASE_WOUND_PROBABILITY = Fraction(1, 6)


@dataclass(frozen=True)
class MorgulArrowsState:
    """Immutable state, with first-affliction turn per surviving enemy."""
    afflicted: tuple[tuple[str, int], ...] = ()
    last_resolved_end_phase: int = 0
    dashboard_score: None = None
    scenario_score: None = None


@dataclass(frozen=True)
class MorgulArrowsEndPhase:
    turn: int
    rolled_model_ids: tuple[str, ...]
    wounded_model_ids: tuple[str, ...]
    wound_probability_per_roll: Fraction = END_PHASE_WOUND_PROBABILITY
    status: str = "explicit_dice_results_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def _turn(turn: int) -> None:
    if type(turn) is not int or turn < 1:
        raise ValueError("turn must be a positive integer")


def _model_id(model_id: str) -> None:
    if not isinstance(model_id, str) or not model_id.strip():
        raise ValueError("model_id must be nonblank")


def register_shooting_wound(
    state: MorgulArrowsState, *, turn: int, target_model_id: str,
    army_list_id: str, active_army_rule_ids: tuple[str, ...],
    attacker_is_friendly: bool, target_is_enemy: bool,
    attack_is_shooting: bool, wound_not_prevented: bool,
) -> MorgulArrowsState:
    """Register a qualifying shooting Wound; repeat Wounds do not stack."""
    if not isinstance(state, MorgulArrowsState):
        raise TypeError("state must be MorgulArrowsState")
    _turn(turn)
    _model_id(target_model_id)
    if turn <= state.last_resolved_end_phase:
        raise ValueError("Cannot register a Wound after its turn's End Phase")
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be nonblank")
    if not isinstance(active_army_rule_ids, tuple) or any(
        not isinstance(x, str) or not x.strip() for x in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a tuple of nonblank IDs")
    flags = (attacker_is_friendly, target_is_enemy, attack_is_shooting, wound_not_prevented)
    if any(type(flag) is not bool for flag in flags):
        raise TypeError("Wound qualification flags must be boolean")
    qualifies = (army_list_id == ARMY_LIST_ID and RULE_ID in active_army_rule_ids
                 and all(flags))
    if not qualifies or target_model_id in dict(state.afflicted):
        return state
    return MorgulArrowsState(
        afflicted=state.afflicted + ((target_model_id, turn),),
        last_resolved_end_phase=state.last_resolved_end_phase,
    )


def resolve_end_phase(
    state: MorgulArrowsState, *, turn: int,
    dice_by_model_id: dict[str, int],
) -> tuple[MorgulArrowsState, MorgulArrowsEndPhase]:
    """Resolve exactly one D6 per eligible model with explicit dice results.

    Afflictions acquired during the current turn do not roll yet. No auto-dice
    are generated; the complete exact set of eligible model IDs is required.
    """
    if not isinstance(state, MorgulArrowsState):
        raise TypeError("state must be MorgulArrowsState")
    _turn(turn)
    if turn <= state.last_resolved_end_phase:
        raise ValueError("End Phase already resolved or out of order")
    if not isinstance(dice_by_model_id, dict):
        raise TypeError("dice_by_model_id must be a dict")
    eligible = tuple(mid for mid, onset in state.afflicted if onset < turn)
    if set(dice_by_model_id) != set(eligible):
        raise ValueError("Exactly one die result per eligible afflicted model required")
    if any(type(die) is not int or not 1 <= die <= 6 for die in dice_by_model_id.values()):
        raise ValueError("Every die result must be an integer from 1 to 6")
    newly_wounded = tuple(mid for mid in eligible if dice_by_model_id[mid] == 1)
    new_state = MorgulArrowsState(state.afflicted, turn)
    result = MorgulArrowsEndPhase(turn, eligible, newly_wounded)
    return new_state, result


def remove_model(state: MorgulArrowsState, *, model_id: str) -> MorgulArrowsState:
    """Remove a casualty or model otherwise leaving the battlefield."""
    if not isinstance(state, MorgulArrowsState):
        raise TypeError("state must be MorgulArrowsState")
    _model_id(model_id)
    return MorgulArrowsState(
        tuple(item for item in state.afflicted if item[0] != model_id),
        state.last_resolved_end_phase,
    )
