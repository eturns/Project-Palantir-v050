"""DEV-077S-I2-G2-C2: joint target-specific shooting evidence.

Independent standard single-wound shots only. Uses C1 to validate and
calculate each shooter's permitted shot count and per-shot wound chance.
No GUI/scenario score changes.
"""
from dataclasses import dataclass
from fractions import Fraction

from defensive_state import DefensiveState
from hero_hunting_shooting import calculate_hero_hunting_shooting_evidence
from hero_hunting_lethal_aim_volley import calculate_lethal_aim_volley_evidence
from lethal_aim import has_lethal_aim
from lethal_aim_state import LethalAimState, LethalAimSpend
from survival_probability import get_survival_probability_after_wounds


@dataclass(frozen=True)
class FocusedShooter:
    shooter_id: str
    attacker: object
    weapon: object
    context: object
    clear_line_of_sight: bool
    in_the_way_required_rolls: tuple[int, ...] = ()
    cavalry_part_in_the_way_required_roll: int | None = None
    target_is_cavalry: bool = False
    lethal_aim_state: LethalAimState | None = None
    lethal_aim_spend: LethalAimSpend | None = None
    lethal_aim_shot_index: int | None = None


@dataclass(frozen=True)
class ConcentratedFireEvidence:
    total_shots: int
    expected_wounds: Fraction
    elimination_probability: Fraction
    incoming_wound_distribution: tuple[Fraction, ...]
    shooter_count: int
    evidence_status: str = "mechanical_complete_for_declared_context"


def calculate_concentrated_fire_evidence(
    *,
    shooters: tuple[FocusedShooter, ...],
    defender: object,
    defender_state: DefensiveState,
    defender_might_for_fate: int = 0,
) -> ConcentratedFireEvidence:
    """Convolve each shooter's wound distribution before resolving Fate once.

    Shooter identities must represent distinct fielded models. Independent
    per-shot events and a single common defensive state are assumed.
    """
    if not shooters:
        raise ValueError("Incomplete Hero Hunting: at least one shooter required.")
    ids = [s.shooter_id for s in shooters]
    if any(not isinstance(x, str) or not x.strip() for x in ids):
        raise ValueError("Incomplete Hero Hunting: shooter identity required.")
    if len(set(ids)) != len(ids):
        raise ValueError("Incomplete Hero Hunting: duplicated shooter identity.")
    if defender_might_for_fate < 0:
        raise ValueError("Defender Might cannot be negative.")

    distribution = (Fraction(1),)
    total_shots = 0
    expected = Fraction(0)
    for shooter in shooters:
        allocated = (shooter.lethal_aim_state is not None
                     or shooter.lethal_aim_spend is not None
                     or shooter.lethal_aim_shot_index is not None)
        if has_lethal_aim(shooter.attacker):
            if not allocated or any(value is None for value in (
                shooter.lethal_aim_state, shooter.lethal_aim_spend,
                shooter.lethal_aim_shot_index,
            )):
                raise ValueError(
                    "Incomplete Hero Hunting: Lethal Aim allocation required for shooter."
                )
            # C5A has no cavalry-part or target-cavalry support. Do not
            # silently drop either shooting condition.
            if (shooter.cavalry_part_in_the_way_required_roll is not None
                    or shooter.target_is_cavalry):
                raise ValueError(
                    "Incomplete Hero Hunting: Lethal Aim cavalry context unsupported."
                )
            volley = calculate_lethal_aim_volley_evidence(
                attacker=shooter.attacker, defender=defender,
                weapon=shooter.weapon, defender_state=defender_state,
                context=shooter.context,
                clear_line_of_sight=shooter.clear_line_of_sight,
                lethal_aim_state=shooter.lethal_aim_state,
                lethal_aim_spend=shooter.lethal_aim_spend,
                lethal_aim_shot_index=shooter.lethal_aim_shot_index,
                in_the_way_required_rolls=shooter.in_the_way_required_rolls,
                defender_might_for_fate=defender_might_for_fate,
            )
            probabilities = volley.shot_wound_probabilities
        else:
            if allocated:
                raise ValueError(
                    "Incomplete Hero Hunting: non-Lethal Aim shooter has allocation."
                )
            one = calculate_hero_hunting_shooting_evidence(
                attacker=shooter.attacker,
                defender=defender,
                weapon=shooter.weapon,
                defender_state=defender_state,
                context=shooter.context,
                clear_line_of_sight=shooter.clear_line_of_sight,
                in_the_way_required_rolls=shooter.in_the_way_required_rolls,
                cavalry_part_in_the_way_required_roll=(
                    shooter.cavalry_part_in_the_way_required_roll
                ),
                target_is_cavalry=shooter.target_is_cavalry,
                defender_might_for_fate=defender_might_for_fate,
            )
            probabilities = (one.wound_probability_per_shot,) * one.shots

        total_shots += len(probabilities)
        expected += sum(probabilities, Fraction(0))
        for p in probabilities:
            updated = [Fraction(0)] * (len(distribution) + 1)
            for count, probability in enumerate(distribution):
                updated[count] += probability * (1 - p)
                updated[count + 1] += probability * p
            distribution = tuple(updated)

    elimination = sum(
        (
            chance * (
                1 - get_survival_probability_after_wounds(
                    defender_state, wounds, might_points=defender_might_for_fate
                )
            )
            for wounds, chance in enumerate(distribution)
        ),
        Fraction(0),
    )
    return ConcentratedFireEvidence(
        total_shots=total_shots,
        expected_wounds=expected,
        elimination_probability=elimination,
        incoming_wound_distribution=distribution,
        shooter_count=len(shooters),
    )
