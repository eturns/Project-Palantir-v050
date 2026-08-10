def get_master_of_the_nazgul_range(
    remaining_will: int,
) -> int:
    if remaining_will < 0:
        raise ValueError(
            "Remaining Will cannot be negative."
        )

    if remaining_will >= 20:
        return 18

    if remaining_will >= 10:
        return 12

    return 6

def is_within_master_of_the_nazgul_range(
    remaining_will: int,
    distance_inches: float,
) -> bool:
    if distance_inches < 0:
        raise ValueError(
            "Distance cannot be negative."
        )

    active_range = get_master_of_the_nazgul_range(
        remaining_will,
    )

    return distance_inches <= active_range

def get_master_of_the_nazgul_resurrection_modifier(
    remaining_will: int,
    distance_inches: float,
) -> int:
    if is_within_master_of_the_nazgul_range(
        remaining_will=remaining_will,
        distance_inches=distance_inches,
    ):
        return 1

    return 0