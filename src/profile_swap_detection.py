"""
Project Palantír
================

File:
    profile_swap_detection.py

Purpose:
    Detects whether two optimiser candidate armies differ by exactly
    one removed profile instance and one added profile instance.

Created:
    DEV-054 – Explainable Recommendations
"""

from optimiser_candidate import OptimiserCandidate
from profile_swap import ProfileSwap


def _profile_quantities(
    candidate: OptimiserCandidate,
) -> dict[str, int]:
    """
    Returns profile quantities keyed by profile id.
    """

    return {
        entry.profile.id: entry.quantity
        for entry in candidate.army.entries
    }


def detect_profile_swap(
    original: OptimiserCandidate,
    alternative: OptimiserCandidate,
) -> ProfileSwap | None:
    """
    Returns the one-for-one profile swap between two candidates.

    A valid swap must:
    - remove exactly one model instance;
    - add exactly one different model instance;
    - leave all other profile quantities unchanged.

    Returns None when the candidates do not differ by exactly one swap.
    """

    original_quantities = _profile_quantities(
        original,
    )

    alternative_quantities = _profile_quantities(
        alternative,
    )

    profile_ids = (
        set(original_quantities)
        | set(alternative_quantities)
    )

    removed_profile_ids = []
    added_profile_ids = []

    for profile_id in profile_ids:
        original_quantity = original_quantities.get(
            profile_id,
            0,
        )

        alternative_quantity = alternative_quantities.get(
            profile_id,
            0,
        )

        difference = (
            alternative_quantity
            - original_quantity
        )

        if difference < 0:
            removed_profile_ids.extend(
                [profile_id] * abs(difference)
            )

        elif difference > 0:
            added_profile_ids.extend(
                [profile_id] * difference
            )

    if len(removed_profile_ids) != 1:
        return None

    if len(added_profile_ids) != 1:
        return None

    return ProfileSwap(
        removed_profile_id=removed_profile_ids[0],
        added_profile_id=added_profile_ids[0],
    )