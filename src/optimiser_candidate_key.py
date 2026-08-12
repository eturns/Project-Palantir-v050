"""
Project Palantír
================

File:
    optimiser_candidate_key.py

Purpose:
    Builds a deterministic identity key for an optimiser candidate
    from its profile ids and quantities.

Created:
    DEV-054 – Explainable Recommendations
"""

from optimiser_candidate import OptimiserCandidate


def build_candidate_key(
    candidate: OptimiserCandidate,
) -> str:
    """
    Returns a deterministic composition key for an optimiser candidate.

    Entry order does not affect the resulting key.
    """

    parts = sorted(
        (
            entry.profile.id,
            entry.quantity,
        )
        for entry in candidate.army.entries
    )

    return "|".join(
        f"{profile_id}:{quantity}"
        for profile_id, quantity in parts
    )