PACING_WEIGHT = 0.70
FINAL_UTILISATION_WEIGHT = 0.30


def calculate_resource_pacing_score(
    starting_resource: int,
    remaining_by_turn: tuple[int, ...],
) -> float:
    if starting_resource < 0:
        raise ValueError(
            "Starting resource cannot be negative."
        )

    if not remaining_by_turn:
        raise ValueError(
            "At least one turn of resource data is required."
        )

    if starting_resource == 0:
        return 1.0

    turn_count = len(remaining_by_turn)

    ideal_remaining = tuple(
        starting_resource
        * (turn_count - turn_number)
        / turn_count
        for turn_number in range(
            1,
            turn_count + 1,
        )
    )

    maximum_possible_deviation = float(
        starting_resource
    )

    largest_deviation = max(
        abs(
            actual - ideal
        )
        for actual, ideal
        in zip(
            remaining_by_turn,
            ideal_remaining,
        )
    )

    pacing_quality = (
        1.0
        - (
            largest_deviation
            / maximum_possible_deviation
        )
    )

    final_remaining = remaining_by_turn[-1]

    final_utilisation = (
        1.0
        - (
            final_remaining
            / starting_resource
        )
    )

    pacing_quality = min(
        max(
            pacing_quality,
            0.0,
        ),
        1.0,
    )

    final_utilisation = min(
        max(
            final_utilisation,
            0.0,
        ),
        1.0,
    )

    score = (
        pacing_quality
        * PACING_WEIGHT
        + final_utilisation
        * FINAL_UTILISATION_WEIGHT
    )

    return min(
        max(
            score,
            0.0,
        ),
        1.0,
    )