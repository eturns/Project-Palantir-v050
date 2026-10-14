"""DEV-077S-I2-G2-C5A: per-shot Lethal Aim volley evidence.

Diagnostic only. Does not alter accepted C1-C4 or any dashboard scoring.
"""
from dataclasses import dataclass
from fractions import Fraction

from defensive_state import DefensiveState
from lethal_aim import (
    has_lethal_aim, can_use_lethal_aim, get_lethal_aim_hit_modifier,
    get_lethal_aim_in_the_way_modifier, get_lethal_aim_wound_modifier,
)
from lethal_aim_state import LethalAimSpend, LethalAimState
from shooting_attack_count import get_effective_shooting_attack_count
from shooting_eligibility import ShootingContext, can_shoot
from shooting_to_hit_modifier import get_movement_shooting_modifier
from shooting_wound_probability import get_shooting_wound_probability
from survival_probability import get_survival_probability_after_wounds
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from wound_modifier import WoundModifier


@dataclass(frozen=True)
class LethalAimVolleyEvidence:
    shots: int
    shot_wound_probabilities: tuple[Fraction, ...]
    incoming_wound_distribution: tuple[Fraction, ...]
    expected_wounds: Fraction
    elimination_probability: Fraction
    evidence_status: str = "mechanical_complete_for_declared_context"


def calculate_lethal_aim_volley_evidence(
    *, attacker, defender, weapon, defender_state: DefensiveState,
    context: ShootingContext, clear_line_of_sight: bool,
    lethal_aim_state: LethalAimState,
    lethal_aim_spend: LethalAimSpend,
    lethal_aim_shot_index: int,
    in_the_way_required_rolls: tuple[int, ...] = (),
    defender_might_for_fate: int = 0,
) -> LethalAimVolleyEvidence:
    """One allocated Lethal Aim spend across a model's full shooting volley.

    Each shot resolves independently, with the free Might used on exactly one
    explicitly selected shot. Fate resolves once against the total wounds.
    Does not model conditional Might decisions after observing a dice roll.
    """
    if not has_lethal_aim(attacker):
        raise ValueError("Incomplete Hero Hunting: attacker lacks Lethal Aim.")
    if context.target_distance_inches is None or not clear_line_of_sight:
        raise ValueError("Incomplete Hero Hunting: explicit range and line of sight required.")
    if not weapon.is_mechanically_complete:
        raise ValueError("Incomplete Hero Hunting: ranged weapon mechanics.")
    if not any(w.id == weapon.wargear_id for w in attacker.effective_wargear):
        raise ValueError("Incomplete Hero Hunting: selected ranged weapon not owned.")
    if not can_shoot(shooter=attacker, weapon=weapon, context=context):
        raise ValueError("Incomplete Hero Hunting: shooter cannot fire in this context.")
    if defender_state.remaining_will:
        raise ValueError("Incomplete Hero Hunting: Will-as-Fate unresolved.")
    if defender_might_for_fate < 0:
        raise ValueError("Defender Might cannot be negative.")
    wound_context = WoundContext(attack_type=WoundAttackType.SHOOTING)
    if not can_use_lethal_aim(
        attacker, lethal_aim_state, lethal_aim_spend, context=wound_context
    ):
        raise ValueError("Incomplete Hero Hunting: invalid Lethal Aim spend.")
    shots = weapon.shots * get_effective_shooting_attack_count(attacker)
    if not isinstance(lethal_aim_shot_index, int) or isinstance(lethal_aim_shot_index, bool) or not 0 <= lethal_aim_shot_index < shots:
        raise ValueError("Incomplete Hero Hunting: invalid Lethal Aim shot index.")
    per_shot = []
    distribution = (Fraction(1),)
    movement = get_movement_shooting_modifier(attacker, moved_this_turn=context.moved_this_turn)
    for index in range(shots):
        selected = index == lethal_aim_shot_index
        spend = lethal_aim_spend if selected else None
        probability = get_shooting_wound_probability(
            attacker=attacker, defender=defender, weapon=weapon,
            in_the_way_required_rolls=in_the_way_required_rolls,
            to_hit_modifier=movement + (get_lethal_aim_hit_modifier(attacker, lethal_aim_state, spend=spend) if selected else 0),
            in_the_way_modifier=(get_lethal_aim_in_the_way_modifier(attacker, lethal_aim_state, spend=spend) if selected else 0),
            wound_modifier=(get_lethal_aim_wound_modifier(attacker, lethal_aim_state, context=wound_context, spend=spend) if selected else WoundModifier()),
        )
        per_shot.append(probability)
        updated = [Fraction(0)] * (len(distribution) + 1)
        for count, existing in enumerate(distribution):
            updated[count] += existing * (1 - probability)
            updated[count + 1] += existing * probability
        distribution = tuple(updated)
    elimination = sum(
        (chance * (1 - get_survival_probability_after_wounds(
            defender_state, wounds, might_points=defender_might_for_fate
        )) for wounds, chance in enumerate(distribution)),
        Fraction(0),
    )
    return LethalAimVolleyEvidence(
        shots=shots, shot_wound_probabilities=tuple(per_shot),
        incoming_wound_distribution=distribution,
        expected_wounds=sum(per_shot, Fraction(0)),
        elimination_probability=elimination,
    )
