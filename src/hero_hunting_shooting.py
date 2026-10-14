"""DEV-077S-I2-G2-C1: isolated, target-specific shooting evidence.

No dashboard/scenario scoring changes. This models independent ordinary
shots from one configured shooter; correlated effects remain unsupported.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import comb

from defensive_state import DefensiveState
from lethal_aim import (
    has_lethal_aim, can_use_lethal_aim,
    get_lethal_aim_hit_modifier, get_lethal_aim_in_the_way_modifier,
    get_lethal_aim_wound_modifier,
)
from lethal_aim_state import LethalAimState, LethalAimSpend
from wound_context import WoundContext
from wound_attack_type import WoundAttackType
from shooting_eligibility import ShootingContext, can_shoot
from shooting_attack_count import get_effective_shooting_attack_count
from shooting_to_hit_modifier import get_movement_shooting_modifier
from shooting_wound_probability import get_shooting_wound_probability
from survival_probability import get_survival_probability_after_wounds


@dataclass(frozen=True)
class ShootingHeroHuntingEvidence:
    shots: int
    wound_probability_per_shot: Fraction
    expected_wounds: Fraction
    elimination_probability: Fraction
    evidence_status: str = "mechanical_complete_for_declared_context"


def calculate_hero_hunting_shooting_evidence(
    *,
    attacker,
    defender,
    weapon,
    defender_state: DefensiveState,
    context: ShootingContext,
    clear_line_of_sight: bool,
    in_the_way_required_rolls: tuple[int, ...] = (),
    cavalry_part_in_the_way_required_roll: int | None = None,
    target_is_cavalry: bool = False,
    defender_might_for_fate: int = 0,
    lethal_aim_state: LethalAimState | None = None,
    lethal_aim_spend: LethalAimSpend | None = None,
) -> ShootingHeroHuntingEvidence:
    """Single-shooter, single-volley target elimination probability.

    Caller supplies explicit range, visibility and all intervening tests.
    Target survival consumes Fate across an incoming-wound distribution.
    """
    if context.target_distance_inches is None:
        raise ValueError("Incomplete Hero Hunting: target range is unknown.")
    if not weapon.is_mechanically_complete:
        raise ValueError("Incomplete Hero Hunting: ranged weapon mechanics.")
    if not clear_line_of_sight:
        raise ValueError("Incomplete Hero Hunting: no clear line of sight.")
    if defender_might_for_fate < 0:
        raise ValueError("Defender Might cannot be negative.")
    if defender_state.remaining_will:
        raise ValueError("Incomplete Hero Hunting: Will-as-Fate must be resolved explicitly.")
    if not any(item.id == weapon.wargear_id for item in attacker.effective_wargear):
        raise ValueError("Incomplete Hero Hunting: selected ranged weapon is not owned.")
    if not can_shoot(shooter=attacker, weapon=weapon, context=context):
        raise ValueError("Incomplete Hero Hunting: shooter cannot fire in this context.")

    shots = weapon.shots * get_effective_shooting_attack_count(attacker)
    if has_lethal_aim(attacker):
        if lethal_aim_spend is None:
            raise ValueError(
                "Incomplete Hero Hunting: Lethal Aim allocation must be explicit."
            )
        if lethal_aim_state is None or not can_use_lethal_aim(
            attacker, lethal_aim_state, lethal_aim_spend,
            context=WoundContext(attack_type=WoundAttackType.SHOOTING),
        ):
            raise ValueError("Incomplete Hero Hunting: invalid Lethal Aim spend.")
        if shots != 1:
            raise ValueError(
                "Incomplete Hero Hunting: Lethal Aim allocation across multiple shots."
            )
    elif lethal_aim_spend is not None or lethal_aim_state is not None:
        raise ValueError("Incomplete Hero Hunting: attacker lacks Lethal Aim.")

    hit_mod = get_lethal_aim_hit_modifier(
        attacker, lethal_aim_state, spend=lethal_aim_spend
    )
    in_way_mod = get_lethal_aim_in_the_way_modifier(
        attacker, lethal_aim_state, spend=lethal_aim_spend
    )
    wound_mod = get_lethal_aim_wound_modifier(
        attacker, lethal_aim_state,
        context=WoundContext(attack_type=WoundAttackType.SHOOTING),
        spend=lethal_aim_spend,
    )
    p = get_shooting_wound_probability(
        attacker=attacker,
        defender=defender,
        weapon=weapon,
        in_the_way_required_rolls=in_the_way_required_rolls,
        in_the_way_modifier=in_way_mod,
        wound_modifier=wound_mod,
        to_hit_modifier=get_movement_shooting_modifier(
            attacker, moved_this_turn=context.moved_this_turn
        ) + hit_mod,
        cavalry_part_in_the_way_required_roll=cavalry_part_in_the_way_required_roll,
        target_is_cavalry=target_is_cavalry,
    )
    # Binomial distribution: independent shots, standard one wound per hit.
    elimination = Fraction(0, 1)
    for wounds in range(shots + 1):
        probability = Fraction(comb(shots, wounds)) * p**wounds * (1-p)**(shots-wounds)
        survival = get_survival_probability_after_wounds(
            defender_state, wounds, might_points=defender_might_for_fate
        )
        elimination += probability * (1 - survival)
    return ShootingHeroHuntingEvidence(
        shots=shots,
        wound_probability_per_shot=p,
        expected_wounds=shots * p,
        elimination_probability=elimination,
    )
