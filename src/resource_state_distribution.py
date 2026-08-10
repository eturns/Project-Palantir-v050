from collections import defaultdict

from hero_resource_state import HeroResourceState
from resistance_resource_state_probability import (
    WeightedHeroResourceState,
)


def combine_weighted_resource_states(
    outcomes: tuple[WeightedHeroResourceState, ...],
) -> tuple[WeightedHeroResourceState, ...]:
    probabilities_by_state = defaultdict(float)

    for outcome in outcomes:
        probabilities_by_state[outcome.state] += (
            outcome.probability
        )

    return tuple(
        WeightedHeroResourceState(
            state=state,
            probability=probability,
        )
        for state, probability in probabilities_by_state.items()
    )


def propagate_resource_distribution(
    outcomes: tuple[WeightedHeroResourceState, ...],
    transition,
) -> tuple[WeightedHeroResourceState, ...]:
    propagated = []

    for outcome in outcomes:
        transitioned_outcomes = transition(
            outcome.state
        )

        for transitioned in transitioned_outcomes:
            propagated.append(
                WeightedHeroResourceState(
                    state=transitioned.state,
                    probability=(
                        outcome.probability
                        * transitioned.probability
                    ),
                )
            )

    return combine_weighted_resource_states(
        tuple(propagated)
    )