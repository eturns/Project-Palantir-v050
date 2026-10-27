"""Mechanical defensive survivability, including conditional wound prevention.

Models with Oblivious to Pain ignore each incoming wound on a natural six.
The prevention test takes place before a wound is accepted or Fate is used;
all other models retain their original transition probabilities.
"""
from fractions import Fraction
from functools import lru_cache

from combat_benchmark import CombatBenchmark
from configured_profile import ConfiguredProfile
from configured_duel_probability import calculate_configured_duel_probability
from configured_wound_probability import calculate_configured_wound_probability
from defensive_state import DefensiveState
from duel_probability import calculate_basic_duel_probability
from fate_probability import get_fate_success_probability
from oblivious_to_pain import prevention_probability
from profiles import Profile
from resurrection_probability import (
    get_resurrection_success_probability,
    get_resurrection_probability_with_necromancer_will,
)
from special_rule_defensive_effect import get_available_fate_attempts
from wound_probability import get_wound_distribution, get_wound_probability
from wound_table import get_wound_target


def _build_benchmark_attacker(benchmark: CombatBenchmark) -> ConfiguredProfile:
    benchmark_profile = Profile(
        id='DEFENCE_BENCHMARK', name='Defence Benchmark', points=0,
        movement=6, fight=benchmark.fight, shooting='4+',
        strength=benchmark.strength, defence=benchmark.defence,
        attacks=benchmark.attacks, wounds=benchmark.wounds,
        courage='4+', intelligence='4+', might=0, will=0,
        fate=0, max_in_army=0,
    )
    return ConfiguredProfile(profile=benchmark_profile)


def _has_unholy_resurrection(profile: Profile | ConfiguredProfile) -> bool:
    assignments = (
        profile.effective_special_rules
        if isinstance(profile, ConfiguredProfile)
        else profile.special_rules
    )
    return any(a.rule.id == 'UNHOLY_RESURRECTION' for a in assignments)


def _get_recovery_probability(*, necromancer_remaining_will: int | None,
                              distance_inches: float | None,
                              will_points_available_to_spend: int) -> Fraction:
    if (not isinstance(will_points_available_to_spend, int)
            or isinstance(will_points_available_to_spend, bool)
            or will_points_available_to_spend < 0):
        raise ValueError('Will points available to spend must be a non-negative integer.')
    has_will = necromancer_remaining_will is not None
    has_distance = distance_inches is not None
    if has_will != has_distance:
        raise ValueError('Necromancer remaining Will and distance must be provided together.')
    if not has_will:
        if will_points_available_to_spend != 0:
            raise ValueError('Will expenditure requires Necromancer Will and distance inputs.')
        return get_resurrection_success_probability()
    return get_resurrection_probability_with_necromancer_will(
        necromancer_remaining_will=necromancer_remaining_will,
        distance_inches=distance_inches,
        will_points_available_to_spend=will_points_available_to_spend,
    )


def calculate_profile_defensive_combat_score(
    profile: Profile | ConfiguredProfile,
    benchmark: CombatBenchmark,
    *,
    engagements: int = 1,
    include_resurrection: bool = False,
    necromancer_remaining_will: int | None = None,
    distance_inches: float | None = None,
    will_points_available_to_spend: int = 0,
    starting_fate: int | None = None,
    starting_will: int | None = None,
) -> float:
    if (not isinstance(engagements, int)
            or isinstance(engagements, bool) or engagements < 1):
        raise ValueError('Engagements must be a positive integer.')
    if not isinstance(include_resurrection, bool):
        raise TypeError('include_resurrection must be a bool.')
    has_recovery_context = (
        necromancer_remaining_will is not None
        or distance_inches is not None
        or will_points_available_to_spend != 0
    )
    if include_resurrection or has_recovery_context:
        resurrection_probability = _get_recovery_probability(
            necromancer_remaining_will=necromancer_remaining_will,
            distance_inches=distance_inches,
            will_points_available_to_spend=will_points_available_to_spend,
        )
    else:
        resurrection_probability = Fraction(0, 1)

    for name, value in (("starting_fate", starting_fate), ("starting_will", starting_will)):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"{name} must be a non-negative integer")
    configured = isinstance(profile, ConfiguredProfile)
    if configured:
        base_profile = profile.profile
        benchmark_attacker = _build_benchmark_attacker(benchmark)
        duel_result = calculate_configured_duel_probability(
            attacker=benchmark_attacker, defender=profile,
        )
        wound_probability = calculate_configured_wound_probability(
            attacker=benchmark_attacker, defender=profile,
        )
    else:
        base_profile = profile
        duel_result = calculate_basic_duel_probability(
            attacker_attacks=benchmark.attacks,
            attacker_fight=benchmark.fight,
            defender_attacks=profile.attacks,
            defender_fight=profile.fight,
        )
        wound_probability = get_wound_probability(get_wound_target(
            strength=benchmark.strength, defence=profile.defence,
        ))

    wound_distribution = get_wound_distribution(
        number_of_strikes=benchmark.attacks,
        wound_probability=wound_probability,
    )
    attacker_win = Fraction(duel_result.attacker_win_probability).limit_denominator(1000000)
    fate_success = get_fate_success_probability()
    fate_failure = 1 - fate_success
    prevent = prevention_probability(profile)
    # Configured defensive profiles can carry purchased per-profile Fate.
    initial_fate = profile.effective_fate if configured else base_profile.fate
    if starting_fate is not None:
        initial_fate = starting_fate
    can_use_will_as_fate = False
    if configured:
        initial_resource_state = DefensiveState(
            remaining_wounds=base_profile.wounds,
            remaining_fate=initial_fate,
            remaining_will=(starting_will if starting_will is not None else profile.effective_will),
        )
        can_use_will_as_fate = (
            get_available_fate_attempts(profile, initial_resource_state)
            > initial_resource_state.remaining_fate
        )
    initial_will = profile.effective_will if configured else base_profile.will
    if starting_will is not None:
        initial_will = starting_will

    @lru_cache(maxsize=None)
    def survive_engagements(engagements_left: int, wounds: int,
                            fate: int, will: int) -> Fraction:
        if wounds <= 0:
            return Fraction(0, 1)
        if engagements_left == 0:
            return Fraction(1, 1)
        defender_win = (1 - attacker_win) * survive_engagements(
            engagements_left - 1, wounds, fate, will,
        )
        attacker_win_result = sum((
            probability * resolve_wounds(
                incoming_wounds, wounds, fate, will,
                engagements_left - 1,
            )
            for incoming_wounds, probability in enumerate(wound_distribution)
        ), Fraction(0, 1))
        return defender_win + attacker_win * attacker_win_result

    @lru_cache(maxsize=None)
    def resolve_wounds(incoming_wounds: int, wounds: int,
                       fate: int, will: int,
                       engagements_after: int, prevention_pending: bool = True) -> Fraction:
        if wounds <= 0:
            return Fraction(0, 1)
        if incoming_wounds == 0:
            return survive_engagements(engagements_after, wounds, fate, will)

        # One prevention roll per incoming wound, even across failed Fate attempts.
        if prevention_pending and prevent:
            prevented = resolve_wounds(
                incoming_wounds - 1, wounds, fate, will, engagements_after,
            )
            unprevented = resolve_wounds(
                incoming_wounds, wounds, fate, will, engagements_after, False,
            )
            return prevent * prevented + (1 - prevent) * unprevented
        accept = resolve_wounds(
            incoming_wounds - 1, wounds - 1, fate, will, engagements_after,
        )
        best = accept
        if fate > 0:
            success = resolve_wounds(
                incoming_wounds - 1, wounds, fate - 1, will,
                engagements_after,
            )
            failure = resolve_wounds(
                incoming_wounds, wounds, fate - 1, will,
                engagements_after, False,
            )
            best = max(best, fate_success * success + fate_failure * failure)
        if can_use_will_as_fate and will > 0:
            success = resolve_wounds(
                incoming_wounds - 1, wounds, fate, will - 1,
                engagements_after,
            )
            failure = resolve_wounds(
                incoming_wounds, wounds, fate, will - 1,
                engagements_after, False,
            )
            best = max(best, fate_success * success + fate_failure * failure)
        return best

    combat_survival = survive_engagements(
        engagements, base_profile.wounds, initial_fate, initial_will,
    )
    if not include_resurrection or not _has_unholy_resurrection(profile):
        return float(combat_survival)
    return float(combat_survival + (1 - combat_survival) * resurrection_probability)


def calculate_fielded_entry_defensive_combat_score(entry, benchmark: CombatBenchmark, **kwargs) -> float:
    # Bridge purchased army-entry resources into the defensive engine.
    if not entry.counts_as_model:
        raise ValueError("Expected model army entry")
    if "starting_fate" in kwargs or "starting_will" in kwargs:
        raise ValueError("Fielded resource input is owned by the army entry")
    return calculate_profile_defensive_combat_score(
        entry.configured_profile, benchmark,
        starting_fate=entry.get_attribute("fate"),
        starting_will=entry.get_attribute("will"), **kwargs,
    )
