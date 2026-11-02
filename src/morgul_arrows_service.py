"""DEV-078-AH-D2 — Morgul Arrows production battlefield-event adapter.

Author: Edward Turns (Project Lead)

Only a fielded friendly shooter's explicitly confirmed, unprevented shooting
Wound can afflict an enemy. Dice and removal events are caller-supplied.
No inferred hits, target profiles, casualties or legacy scoring changes.
"""
from dataclasses import dataclass
from army import Army
from morgul_arrows import (
    ARMY_LIST_ID, RULE_ID, MorgulArrowsState,
    register_shooting_wound, resolve_end_phase, remove_model,
)

@dataclass(frozen=True)
class MorgulArrowsShootingWound:
    turn: int
    attacker_model_id: str
    target_model_id: str
    target_is_enemy: bool
    attack_is_shooting: bool
    wound_not_prevented: bool

@dataclass(frozen=True)
class MorgulArrowsBattlefieldRequest:
    initial_state: MorgulArrowsState = MorgulArrowsState()
    shooting_wounds: tuple[MorgulArrowsShootingWound, ...] = ()
    end_phase_turn: int | None = None
    dice_by_model_id: dict[str, int] | None = None
    removed_model_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class MorgulArrowsArmyEvidence:
    source_rule_id: str
    state: MorgulArrowsState
    end_phase: object | None
    status: str = "explicit_battlefield_events_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def build_morgul_arrows_army_evidence(
    army: Army, army_list, *, request: MorgulArrowsBattlefieldRequest,
) -> MorgulArrowsArmyEvidence:
    if not isinstance(army, Army):
        raise TypeError("Requires a real Army")
    if not isinstance(request, MorgulArrowsBattlefieldRequest):
        raise TypeError("request must be MorgulArrowsBattlefieldRequest")
    if getattr(army_list, "id", None) != ARMY_LIST_ID:
        raise ValueError("Morgul Arrows requires Azog's Hunters")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("Registered army_rules required")
    ids = tuple(getattr(r, "id", None) for r in rules)
    if any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("Invalid army-rule identifiers")
    if RULE_ID not in ids:
        raise ValueError("Morgul Arrows army rule not registered")
    if not isinstance(request.initial_state, MorgulArrowsState):
        raise TypeError("initial_state must be MorgulArrowsState")
    if not isinstance(request.shooting_wounds, tuple) or any(
        not isinstance(w, MorgulArrowsShootingWound) for w in request.shooting_wounds
    ):
        raise TypeError("shooting_wounds must be tuple of MorgulArrowsShootingWound")
    if not isinstance(request.removed_model_ids, tuple) or any(
        not isinstance(mid, str) or not mid.strip() for mid in request.removed_model_ids
    ):
        raise TypeError("removed_model_ids must be tuple of nonblank IDs")
    fielded = {m.id: m for m in army.fielded_models()}
    state = request.initial_state
    for event in request.shooting_wounds:
        if event.attacker_model_id not in fielded:
            raise ValueError("Shooting attacker is not fielded")
        model = fielded[event.attacker_model_id]
        if not model.counts_as_model or model.configured_profile is None:
            raise ValueError("Shooting attacker must be a fielded model")
        state = register_shooting_wound(
            state, turn=event.turn, target_model_id=event.target_model_id,
            army_list_id=army_list.id, active_army_rule_ids=ids,
            attacker_is_friendly=True, target_is_enemy=event.target_is_enemy,
            attack_is_shooting=event.attack_is_shooting,
            wound_not_prevented=event.wound_not_prevented,
        )
    for mid in request.removed_model_ids:
        state = remove_model(state, model_id=mid)
    phase = None
    if request.end_phase_turn is not None:
        if request.dice_by_model_id is None:
            raise ValueError("Explicit dice results required for End Phase")
        state, phase = resolve_end_phase(
            state, turn=request.end_phase_turn,
            dice_by_model_id=request.dice_by_model_id,
        )
    elif request.dice_by_model_id is not None:
        raise ValueError("End Phase turn required with supplied dice")
    return MorgulArrowsArmyEvidence(
        source_rule_id=RULE_ID, state=state, end_phase=phase
    )
