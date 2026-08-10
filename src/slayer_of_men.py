from configured_duel_probability import (
    calculate_configured_duel_probability,
)

def is_slayer_of_men_burly_active(
    distance_to_other_slayer_inches: float,
) -> bool:
    if distance_to_other_slayer_inches < 0:
        raise ValueError(
            "Distance to other Slayer cannot be negative."
        )

    return distance_to_other_slayer_inches <= 1

def calculate_slayer_of_men_duel_probability(
    attacker,
    defender,
    distance_to_other_slayer_inches: float,
    attacker_selection=None,
    defender_selection=None,
):
    return calculate_configured_duel_probability(
        attacker=attacker,
        defender=defender,
        attacker_selection=attacker_selection,
        defender_selection=defender_selection,
        attacker_additional_burly=(
            is_slayer_of_men_burly_active(
                distance_to_other_slayer_inches
            )
        ),
    )