def improve_magical_test_roll(
    roll: int,
    might_to_spend: int,
) -> int:
    if not 1 <= roll <= 6:
        raise ValueError(
            "Magical test roll must be between 1 and 6."
        )

    if might_to_spend < 0:
        raise ValueError(
            "Might spend cannot be negative."
        )

    return min(
        6,
        roll + might_to_spend,
    )