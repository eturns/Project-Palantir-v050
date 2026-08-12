BALANCED_MEAN_WEIGHT = 0.75
BALANCED_MINIMUM_WEIGHT = 0.25


def calculate_balanced_score(
    component_scores: tuple[float, ...],
) -> float:
    if not component_scores:
        raise ValueError(
            "Balanced score requires at least one component."
        )

    mean_score = (
        sum(component_scores)
        / len(component_scores)
    )

    minimum_score = min(
        component_scores,
    )

    return (
        mean_score * BALANCED_MEAN_WEIGHT
        + minimum_score * BALANCED_MINIMUM_WEIGHT
    )