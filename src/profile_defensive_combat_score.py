"""DEV-077S-I2-C-G7-C2: Mechanical defensive survivability.

Supports:
- Configured Duel and Wound probability
- Repeated engagements
- Stateful Wounds, Fate and permitted Will-as-Fate
- Optional Unholy Resurrection recovery
- Master of the Nazgul support
- Explicit Necromancer Will expenditure

Resurrection represents one post-defeat recovery opportunity,
not additional Wounds or guaranteed battlefield availability.
"""

from fractions import Fraction
from functools import lru_cache

from combat_benchmark import CombatBenchmark
from configured_profile import ConfiguredProfile
from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from configured_wound_probability import (
    calculate_configured_wound_probability,
)
from defensive_state import DefensiveState
from duel_probability import (
    calculate_basic_duel_probability,
)
from fate_probability import (
    get_fate_success_probability,
)
from profiles import Profile
from resurrection_probability import (
    get_resurrection_success_probability,
    get_resurrection_probability_with_necromancer_will,
)
from special_rule_defensive_effect import (
    get_available_fate_attempts,
)
from wound_probability import (
    get_wound_distribution,
    get_wound_probability,
)
from wound_table import get_wound_target


def _build_benchmark_attacker(
    benchmark: CombatBenchmark,
) -> ConfiguredProfile:
    """Create the unmodified benchmark combatant."""

    benchmark_profile = Profile(
        id="DEFENCE_BENCHMARK",
        name="Defence Benchmark",
        points=0,
        movement=6,
        fight=benchmark.fight,
        shooting="4+",
        strength=benchmark.strength,
        defence=benchmark.defence,
        attacks=benchmark.attacks,
        wounds=benchmark.wounds,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )

    return ConfiguredProfile(
        profile=benchmark_profile,
    )


def _has_unholy_resurrection(
    profile: Profile | ConfiguredProfile,
) -> bool:
    """Check the effective special-rule assignments."""

    if isinstance(profile, ConfiguredProfile):
        assignments = profile.effective_special_rules
    else:
        assignments = profile.special_rules

    return any(
        assignment.rule.id == "UNHOLY_RESURRECTION"
        for assignment in assignments
    )


def _get_recovery_probability(
    *,
    necromancer_remaining_will: int | None,
    distance_inches: float | None,
    will_points_available_to_spend: int,
) -> Fraction:
    """Resolve one resurrection attempt.

    Without Necromancer context, the standard resurrection
    probability applies.

    When context is supplied, both Will and distance are
    required. Will expenditure is never assumed.
    """

    if (
        not isinstance(will_points_available_to_spend, int)
        or isinstance(will_points_available_to_spend, bool)
        or will_points_available_to_spend < 0
    ):
        raise ValueError(
            "Will points available to spend must "
            "be a non-negative integer."
        )

    has_will_context = (
        necromancer_remaining_will is not None
    )

    has_distance_context = (
        distance_inches is not None
    )

    if has_will_context != has_distance_context:
        raise ValueError(
            "Necromancer remaining Will and distance "
            "must be provided together."
        )

    if not has_will_context:
        if will_points_available_to_spend != 0:
            raise ValueError(
                "Will expenditure requires Necromancer "
                "Will and distance inputs."
            )

        return get_resurrection_success_probability()

    return get_resurrection_probability_with_necromancer_will(
        necromancer_remaining_will=necromancer_remaining_will,
        distance_inches=distance_inches,
        will_points_available_to_spend=(
            will_points_available_to_spend
        ),
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
) -> float:
    """Calculate combat survival or post-recovery presence.

    Combat survival uses repeated benchmark engagements,
    with Wounds, Fate and permitted Will-as-Fate carried
    forward between encounters.

    When resurrection is enabled for a model possessing
    Unholy Resurrection, one recovery opportunity follows
    defeat.

    Necromancer support must be explicitly configured.
    """

    if (
        not isinstance(engagements, int)
        or isinstance(engagements, bool)
        or engagements < 1
    ):
        raise ValueError(
            "Engagements must be a positive integer."
        )

    if not isinstance(include_resurrection, bool):
        raise TypeError(
            "include_resurrection must be a bool."
        )

    # Validate explicit recovery context even when the
    # defender does not possess Unholy Resurrection.
    has_recovery_context = (
        necromancer_remaining_will is not None
        or distance_inches is not None
        or will_points_available_to_spend != 0
    )

    if include_resurrection or has_recovery_context:
        resurrection_probability = (
            _get_recovery_probability(
                necromancer_remaining_will=(
                    necromancer_remaining_will
                ),
                distance_inches=distance_inches,
                will_points_available_to_spend=(
                    will_points_available_to_spend
                ),
            )
        )
    else:
        resurrection_probability = Fraction(0, 1)

    configured = isinstance(
        profile,
        ConfiguredProfile,
    )

    if configured:
        base_profile = profile.profile

        benchmark_attacker = _build_benchmark_attacker(
            benchmark,
        )

        duel_result = (
            calculate_configured_duel_probability(
                attacker=benchmark_attacker,
                defender=profile,
            )
        )

        wound_probability = (
            calculate_configured_wound_probability(
                attacker=benchmark_attacker,
                defender=profile,
            )
        )

    else:
        base_profile = profile

        duel_result = calculate_basic_duel_probability(
            attacker_attacks=benchmark.attacks,
            attacker_fight=benchmark.fight,
            defender_attacks=profile.attacks,
            defender_fight=profile.fight,
        )

        wound_target = get_wound_target(
            strength=benchmark.strength,
            defence=profile.defence,
        )

        wound_probability = get_wound_probability(
            wound_target,
        )

    wound_distribution = get_wound_distribution(
        number_of_strikes=benchmark.attacks,
        wound_probability=wound_probability,
    )

    attacker_win = Fraction(
        duel_result.attacker_win_probability
    ).limit_denominator(1000000)

    fate_success = get_fate_success_probability()
    fate_failure = 1 - fate_success

    can_use_will_as_fate = False

    if configured:
        initial_resource_state = DefensiveState(
            remaining_wounds=base_profile.wounds,
            remaining_fate=base_profile.fate,
            remaining_will=profile.effective_will,
        )

        available_attempts = get_available_fate_attempts(
            profile,
            initial_resource_state,
        )

        can_use_will_as_fate = (
            available_attempts
            > initial_resource_state.remaining_fate
        )

    initial_will = (
        profile.effective_will
        if configured
        else base_profile.will
    )

    @lru_cache(maxsize=None)
    def survive_engagements(
        engagements_left: int,
        wounds: int,
        fate: int,
        will: int,
    ) -> Fraction:

        if wounds <= 0:
            return Fraction(0, 1)

        if engagements_left == 0:
            return Fraction(1, 1)

        defender_win_result = (
            (1 - attacker_win)
            * survive_engagements(
                engagements_left - 1,
                wounds,
                fate,
                will,
            )
        )

        attacker_win_result = sum(
            (
                probability
                * resolve_wounds(
                    incoming_wounds,
                    wounds,
                    fate,
                    will,
                    engagements_left - 1,
                )
            )
            for incoming_wounds, probability
            in enumerate(wound_distribution)
        )

        return (
            defender_win_result
            + attacker_win * attacker_win_result
        )

    @lru_cache(maxsize=None)
    def resolve_wounds(
        incoming_wounds: int,
        wounds: int,
        fate: int,
        will: int,
        engagements_after: int,
    ) -> Fraction:

        if wounds <= 0:
            return Fraction(0, 1)

        if incoming_wounds == 0:
            return survive_engagements(
                engagements_after,
                wounds,
                fate,
                will,
            )

        # The defender may accept the incoming Wound.
        best_survival = resolve_wounds(
            incoming_wounds - 1,
            wounds - 1,
            fate,
            will,
            engagements_after,
        )

        # Spend one Fate point.
        if fate > 0:
            success_result = resolve_wounds(
                incoming_wounds - 1,
                wounds,
                fate - 1,
                will,
                engagements_after,
            )

            failure_result = resolve_wounds(
                incoming_wounds,
                wounds,
                fate - 1,
                will,
                engagements_after,
            )

            fate_result = (
                fate_success * success_result
                + fate_failure * failure_result
            )

            best_survival = max(
                best_survival,
                fate_result,
            )

        # Spend Will as Fate only when permitted.
        if can_use_will_as_fate and will > 0:
            success_result = resolve_wounds(
                incoming_wounds - 1,
                wounds,
                fate,
                will - 1,
                engagements_after,
            )

            failure_result = resolve_wounds(
                incoming_wounds,
                wounds,
                fate,
                will - 1,
                engagements_after,
            )

            will_result = (
                fate_success * success_result
                + fate_failure * failure_result
            )

            best_survival = max(
                best_survival,
                will_result,
            )

        return best_survival

    combat_survival = survive_engagements(
        engagements,
        base_profile.wounds,
        base_profile.fate,
        initial_will,
    )

    if (
        not include_resurrection
        or not _has_unholy_resurrection(profile)
    ):
        return float(combat_survival)

    # One post-defeat recovery opportunity.
    # The resurrection probability includes explicitly
    # configured Necromancer support, if supplied.
    effective_presence = (
        combat_survival
        + (
            Fraction(1, 1) - combat_survival
        ) * resurrection_probability
    )

    return float(effective_presence)