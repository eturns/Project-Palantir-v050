from scenario_capability import ScenarioCapability
from resurrection_probability import (
    get_resurrection_probability_with_necromancer_will,
    get_resurrection_success_probability,
)
from resurrection_recovery import (
    calculate_expected_resurrection_bonus,
)
from resurrection_resilience_modifier import (
    calculate_resurrection_resilience_modifier,
)
from resurrection_state_resilience import (
    apply_resurrection_to_state_resilience,
)


def calculate_resurrection_modified_state_resilience(
    state_resilience: ScenarioCapability,
    resurrection_capable_models: int,
    starting_models: int,
    resilience_weight: int | float,
    necromancer_remaining_will: int | None = None,
    distance_inches: float | None = None,
    will_points_available_to_spend: int = 0,
) -> ScenarioCapability:
    use_necromancer_path = (
        necromancer_remaining_will is not None
        or distance_inches is not None
    )

    if use_necromancer_path:
        if necromancer_remaining_will is None:
            raise ValueError(
                "necromancer_remaining_will is required when "
                "distance_inches is supplied."
            )

        if distance_inches is None:
            raise ValueError(
                "distance_inches is required when "
                "necromancer_remaining_will is supplied."
            )

        success_probability = (
            get_resurrection_probability_with_necromancer_will(
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
        if will_points_available_to_spend != 0:
            raise ValueError(
                "will_points_available_to_spend requires "
                "Necromancer Will and distance inputs."
            )

        success_probability = (
            get_resurrection_success_probability()
        )

    expected_bonus = (
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=(
                resurrection_capable_models
            ),
            starting_models=starting_models,
            success_probability=success_probability,
        )
    )

    resurrection_modifier = (
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=expected_bonus,
            resilience_weight=resilience_weight,
        )
    )

    return apply_resurrection_to_state_resilience(
        state_resilience=state_resilience,
        resurrection_modifier=resurrection_modifier,
    )