"""DEV-077-SMAUG-C3B/E — independent incoming missile volley diagnostic.

Opt-in, source-linked defensive evidence. No scenario/dashboard scoring.
One shot has outcomes 0, 1 or missile Strength wounds, preserving the
original natural-six condition. Convolve all shots BEFORE one Fate calculation.
"""
from dataclasses import dataclass
from fractions import Fraction
from defensive_state import DefensiveState
from survival_probability import get_survival_probability_after_wounds
from smaug_missing_scale import calculate_missing_scale_evidence


@dataclass(frozen=True)
class IncomingMissile:
    shooter_id: str
    shoot_value: str
    missile_strength: int
    shots: int = 1
    to_hit_modifier: int = 0


@dataclass(frozen=True)
class MissingScaleVolleyEvidence:
    incoming_wound_distribution: tuple[Fraction, ...]
    expected_incoming_wounds: Fraction
    elimination_probability: Fraction
    shot_count: int
    status: str = "bounded_independent_missiles_scoring_unchanged"
    dashboard_score: None = None
    scenario_score: None = None


def calculate_smaug_missing_scale_volley(
    *, target_profile_id: str, shooters: tuple[IncomingMissile, ...],
    state: DefensiveState, defender_might_for_fate: int = 0,
    target_defence: int = 9,
) -> MissingScaleVolleyEvidence:
    if target_profile_id != "SMAUG":
        raise ValueError("Missing Scale volley is restricted to Smaug")
    if not isinstance(shooters, tuple) or not shooters:
        raise ValueError("At least one declared shooter is required")
    if not isinstance(state, DefensiveState):
        raise TypeError("state must be DefensiveState")
    if state.remaining_will:
        raise ValueError("Will-as-Fate is unsupported")
    if type(defender_might_for_fate) is not int or defender_might_for_fate < 0:
        raise ValueError("Invalid defender Might")
    ids = [s.shooter_id for s in shooters if isinstance(s, IncomingMissile)]
    if len(ids) != len(shooters) or any(not x.strip() for x in ids) or len(set(ids)) != len(ids):
        raise ValueError("Each shooter requires a distinct identifier")
    distribution = (Fraction(1),)
    count = 0
    for shooter in shooters:
        if type(shooter.shots) is not int or shooter.shots < 1:
            raise ValueError("Shots must be positive integers")
        single = calculate_missing_scale_evidence(
            shooter_shoot_value=shooter.shoot_value,
            missile_strength=shooter.missile_strength,
            smaug_defence=target_defence,
            to_hit_modifier=shooter.to_hit_modifier,
            smaug_state=state,
            smaug_might_for_fate=defender_might_for_fate,
        )
        shot_dist = [Fraction(0)] * (shooter.missile_strength + 1)
        shot_dist[0] = single.miss_or_no_wound_probability
        shot_dist[1] += single.ordinary_wound_probability
        shot_dist[shooter.missile_strength] += single.missing_scale_wound_probability
        for _ in range(shooter.shots):
            next_dist = [Fraction(0)] * (len(distribution) + len(shot_dist) - 1)
            for i, p in enumerate(distribution):
                for j, q in enumerate(shot_dist):
                    next_dist[i+j] += p*q
            distribution = tuple(next_dist)
            count += 1
    expected = sum((i*x for i,x in enumerate(distribution)), Fraction(0))
    elimination = sum((
        probability * (
            1 - get_survival_probability_after_wounds(
                state, incoming_wounds=wounds,
                might_points=defender_might_for_fate,
            )
        )
        for wounds, probability in enumerate(distribution)
    ), Fraction(0))
    return MissingScaleVolleyEvidence(distribution, expected, elimination, count)
