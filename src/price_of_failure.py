from itertools import (
    combinations,
    product,
)

from price_of_failure_state import (
    PriceOfFailureState,
)
from duel_probability_result import (
    DuelProbabilityResult,
)
from duel_modifier import (
    DuelModifier,
    apply_duel_modifier_to_rolls,
)

PRICE_OF_FAILURE_RULE_ID = "PRICE_OF_FAILURE"

def has_price_of_failure(
    profile,
) -> bool:
    configured_profile = (
        profile.active_configured_profile
        if hasattr(
            profile,
            "active_configured_profile",
        )
        else profile
    )

    return any(
        assignment.rule.id
        == PRICE_OF_FAILURE_RULE_ID
        for assignment
        in configured_profile.effective_special_rules
    )

def apply_price_of_failure_reroll(
    rolls: tuple[int, ...],
    reroll_indexes: tuple[int, ...],
    replacement_rolls: tuple[int, ...],
) -> tuple[int, ...]:
    if not rolls:
        raise ValueError(
            "At least one Duel die is required."
        )

    if len(reroll_indexes) != len(
        replacement_rolls
    ):
        raise ValueError(
            "Replacement rolls must match "
            "the number of rerolled dice."
        )

    if len(set(reroll_indexes)) != len(
        reroll_indexes
    ):
        raise ValueError(
            "A Duel die cannot be rerolled twice."
        )

    for index in reroll_indexes:
        if not 0 <= index < len(rolls):
            raise ValueError(
                "Reroll index is outside the Duel dice."
            )

    for replacement_roll in replacement_rolls:
        if not 1 <= replacement_roll <= 6:
            raise ValueError(
                "Replacement Duel rolls must be "
                "between 1 and 6."
            )

    updated_rolls = list(rolls)

    for index, replacement_roll in zip(
        reroll_indexes,
        replacement_rolls,
    ):
        updated_rolls[index] = replacement_roll

    return tuple(updated_rolls)


def generate_price_of_failure_reroll_outcomes(
    rolls: tuple[int, ...],
    reroll_indexes: tuple[int, ...],
    state: PriceOfFailureState,
) -> tuple[tuple[int, ...], ...]:
    if not state.can_use:
        return (
            rolls,
        )

    if not reroll_indexes:
        return (
            rolls,
        )

    return tuple(
        apply_price_of_failure_reroll(
            rolls=rolls,
            reroll_indexes=reroll_indexes,
            replacement_rolls=replacements,
        )
        for replacements in product(
            range(1, 7),
            repeat=len(reroll_indexes),
        )
    )

def choose_price_of_failure_reroll_indexes(
    rolls: tuple[int, ...],
) -> tuple[int, ...]:
    if not rolls:
        raise ValueError(
            "At least one Duel die is required."
        )

    highest_roll = max(rolls)

    if highest_roll == 6:
        return ()

    highest_index = rolls.index(
        highest_roll
    )

    return tuple(
        index
        for index in range(len(rolls))
        if index != highest_index
    )

def generate_price_of_failure_reroll_index_choices(
    rolls: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    if not rolls:
        raise ValueError(
            "At least one Duel die is required."
        )

    indexes = tuple(
        range(len(rolls))
    )

    return tuple(
        choice
        for reroll_count in range(
            len(indexes) + 1
        )
        for choice in combinations(
            indexes,
            reroll_count,
        )
    )


def _duel_roll_wins(
    *,
    attacker_rolls: tuple[int, ...],
    defender_rolls: tuple[int, ...],
    attacker_fight: int,
    defender_fight: int,
    attacker_roll_off_probability: float,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
) -> float:
    modified_attacker_rolls = (
        apply_duel_modifier_to_rolls(
            attacker_rolls,
            attacker_modifier,
        )
        if attacker_modifier is not None
        else attacker_rolls
    )

    modified_defender_rolls = (
        apply_duel_modifier_to_rolls(
            defender_rolls,
            defender_modifier,
        )
        if defender_modifier is not None
        else defender_rolls
    )

    attacker_highest = max(
        modified_attacker_rolls
    )
    defender_highest = max(
        modified_defender_rolls
    )

    if attacker_highest > defender_highest:
        return 1.0

    if attacker_highest < defender_highest:
        return 0.0

    if attacker_fight > defender_fight:
        return 1.0

    if attacker_fight < defender_fight:
        return 0.0

    return attacker_roll_off_probability

def calculate_price_of_failure_choice_win_probability(
    *,
    attacker_rolls: tuple[int, ...],
    defender_rolls: tuple[int, ...],
    reroll_indexes: tuple[int, ...],
    attacker_fight: int,
    defender_fight: int,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
    attacker_roll_off_probability: float = 0.5,
) -> float:
    if not 0.0 <= attacker_roll_off_probability <= 1.0:
        raise ValueError(
            "Attacker roll-off probability must be "
            "between 0 and 1."
        )

    state = PriceOfFailureState(
        declared=True,
        within_azog_range=True,
    )

    outcomes = (
        generate_price_of_failure_reroll_outcomes(
            rolls=attacker_rolls,
            reroll_indexes=reroll_indexes,
            state=state,
        )
    )

    return sum(
        _duel_roll_wins(
            attacker_rolls=outcome,
            defender_rolls=defender_rolls,
            attacker_fight=attacker_fight,
            defender_fight=defender_fight,
            attacker_modifier=attacker_modifier,
            defender_modifier=defender_modifier,
            attacker_roll_off_probability=(
                attacker_roll_off_probability
            ),
        )
        for outcome in outcomes
    ) / len(outcomes)


def choose_optimal_price_of_failure_reroll_indexes(
    *,
    attacker_rolls: tuple[int, ...],
    defender_rolls: tuple[int, ...],
    attacker_fight: int,
    defender_fight: int,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
    attacker_roll_off_probability: float = 0.5,
) -> tuple[int, ...]:
    choices = (
        generate_price_of_failure_reroll_index_choices(
            attacker_rolls
        )
    )

    return max(
        choices,
        key=lambda choice: (
            calculate_price_of_failure_choice_win_probability(
                attacker_rolls=attacker_rolls,
                defender_rolls=defender_rolls,
                reroll_indexes=choice,
                attacker_fight=attacker_fight,
                defender_fight=defender_fight,
                attacker_modifier=attacker_modifier,
                defender_modifier=defender_modifier,
                attacker_roll_off_probability=(
                    attacker_roll_off_probability
                ),
            ),
            -len(choice),
        ),
    )

def calculate_price_of_failure_duel_probability(
    *,
    attacker_attacks: int,
    attacker_fight: int,
    defender_attacks: int,
    defender_fight: int,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
    state: PriceOfFailureState,
    attacker_roll_off_probability: float = 0.5,
) -> DuelProbabilityResult:
    if attacker_attacks < 1:
        raise ValueError(
            "Attacker must roll at least one Duel die."
        )

    if defender_attacks < 1:
        raise ValueError(
            "Defender must roll at least one Duel die."
        )

    if not 0.0 <= attacker_roll_off_probability <= 1.0:
        raise ValueError(
            "Attacker roll-off probability must be "
            "between 0 and 1."
        )

    attacker_initial_outcomes = tuple(
        tuple(rolls)
        for rolls in product(
            range(1, 7),
            repeat=attacker_attacks,
        )
    )

    defender_initial_outcomes = tuple(
        tuple(rolls)
        for rolls in product(
            range(1, 7),
            repeat=defender_attacks,
        )
    )

    initial_outcome_weight = (
        1.0
        / (
            len(attacker_initial_outcomes)
            * len(defender_initial_outcomes)
        )
    )

    attacker_win_probability = 0.0
    defender_win_probability = 0.0

    for attacker_rolls in attacker_initial_outcomes:
        for defender_rolls in defender_initial_outcomes:
            if state.can_use:
                reroll_indexes = (
                    choose_optimal_price_of_failure_reroll_indexes(
                        attacker_rolls=attacker_rolls,
                        defender_rolls=defender_rolls,
                        attacker_fight=attacker_fight,
                        defender_fight=defender_fight,
                        attacker_modifier=attacker_modifier,
                        defender_modifier=defender_modifier,
                        attacker_roll_off_probability=(
                            attacker_roll_off_probability
                        ),
                    )
                )
            else:
                reroll_indexes = ()

            final_attacker_outcomes = (
                generate_price_of_failure_reroll_outcomes(
                    rolls=attacker_rolls,
                    reroll_indexes=reroll_indexes,
                    state=state,
                )
            )

            reroll_outcome_weight = (
                initial_outcome_weight
                / len(final_attacker_outcomes)
            )

            for final_attacker_rolls in final_attacker_outcomes:
                attacker_win_share = _duel_roll_wins(
                    attacker_rolls=final_attacker_rolls,
                    defender_rolls=defender_rolls,
                    attacker_fight=attacker_fight,
                    defender_fight=defender_fight,
                    attacker_modifier=attacker_modifier,
                    defender_modifier=defender_modifier,
                    attacker_roll_off_probability=(
                        attacker_roll_off_probability
                    ),
                )

                attacker_win_probability += (
                    reroll_outcome_weight
                    * attacker_win_share
                )

                defender_win_probability += (
                    reroll_outcome_weight
                    * (1.0 - attacker_win_share)
                )

    return DuelProbabilityResult(
        attacker_win_probability=(
            attacker_win_probability
        ),
        defender_win_probability=(
            defender_win_probability
        ),
        draw_probability=0.0,
    )