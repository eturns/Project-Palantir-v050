"""DEV-077-SMAUG-D6B — unified, unscored scenario mechanics evidence.

Edward Turns (Project Lead). Opt-in, read-only composition of D2/D4/D5.
The caller supplies scenario positions, legal charges and optional final scores.
This module does NOT modify scenario-fit scores, battlefield state or calibration.
"""
from __future__ import annotations

from dataclasses import dataclass
from smaug_sheer_dominance import (
    SheerDominanceEvidence, evaluate_smaug_sheer_dominance,
)
from smaug_lust_for_gold import (
    LustForGoldEvidence, ObjectiveCarrierChargeTarget, assess_lust_for_gold,
)
from smaug_gold_markers import SmaugGoldState
from smaug_gold_victory_points import (
    SmaugGoldVictoryPointEvidence, calculate_smaug_gold_victory_points,
)


@dataclass(frozen=True)
class SmaugScenarioEvidence:
    smaug_model_id: str
    dominance: SheerDominanceEvidence
    lust_for_gold: LustForGoldEvidence
    gold_marker_state: SmaugGoldState | None
    gold_victory_points: SmaugGoldVictoryPointEvidence | None
    status: str
    dashboard_score: None = None
    scenario_score: None = None


def build_smaug_scenario_evidence(
    *,
    smaug_model_id: str,
    rule_ids: frozenset[str],
    distance_to_objective_inches: float | None = None,
    objective_range_inches: float | None = None,
    moving: bool | None = None,
    charge_targets: tuple[ObjectiveCarrierChargeTarget, ...] | None = None,
    gold_marker_state: SmaugGoldState | None = None,
    game_ended: bool = False,
    smaug_points: int | None = None,
    opponent_points: int | None = None,
) -> SmaugScenarioEvidence:
    """Compose existing evidence without inventing battlefield facts.

    Gold holders are treated as objective carriers for Lust for Gold only
    when an explicit list of charge targets is provided. Charge legality
    remains the caller's responsibility.

    A game-ending score must be supplied explicitly; missing state is not
    interpreted as zero or as the marker's starting allocation.
    """
    if not isinstance(smaug_model_id, str) or not smaug_model_id.strip():
        raise ValueError("smaug_model_id must be a nonblank string")
    if type(game_ended) is not bool:
        raise TypeError("game_ended must be a bool")
    if gold_marker_state is not None:
        if not isinstance(gold_marker_state, SmaugGoldState):
            raise TypeError("gold_marker_state must be SmaugGoldState")
        if gold_marker_state.smaug_model_id != smaug_model_id:
            raise ValueError("Gold state belongs to a different Smaug model")

    if charge_targets is not None:
        if not isinstance(charge_targets, tuple) or not all(
            isinstance(t, ObjectiveCarrierChargeTarget) for t in charge_targets
        ):
            raise TypeError("charge_targets must be a tuple of ObjectiveCarrierChargeTarget")
        if gold_marker_state is not None:
            gold_holders = gold_marker_state.enemy_carrier_ids
            charge_targets = tuple(
                ObjectiveCarrierChargeTarget(
                    model_id=t.model_id,
                    enemy=t.enemy,
                    carries_objective=(t.carries_objective or (t.enemy and t.model_id in gold_holders)),
                    can_charge=t.can_charge,
                )
                for t in charge_targets
            )

    dominance = evaluate_smaug_sheer_dominance(
        profile_id="SMAUG", rule_ids=rule_ids,
        distance_to_objective_inches=distance_to_objective_inches,
        objective_range_inches=objective_range_inches,
    )
    charge = assess_lust_for_gold(
        profile_id="SMAUG", rule_ids=rule_ids,
        targets=charge_targets, moving=moving,
    )
    if game_ended:
        if gold_marker_state is None:
            raise ValueError("Final gold scoring requires Gold Marker state")
        if smaug_points is None or opponent_points is None:
            raise ValueError("Final gold scoring requires both actual VP totals")
        gold_vp = calculate_smaug_gold_victory_points(
            gold_marker_state, smaug_points=smaug_points, opponent_points=opponent_points
        )
    else:
        if smaug_points is not None or opponent_points is not None:
            raise ValueError("Victory-point totals are only accepted at game end")
        gold_vp = None

    status = ("conditional_not_evaluated" if
              dominance.status == "conditional_not_evaluated" or
              charge.status in ("conditional_not_evaluated", "charge_legality_unknown")
              else "evaluated")
    return SmaugScenarioEvidence(
        smaug_model_id=smaug_model_id,
        dominance=dominance,
        lust_for_gold=charge,
        gold_marker_state=gold_marker_state,
        gold_victory_points=gold_vp,
        status=status,
    )
