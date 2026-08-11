"""
Project Palantír
================

File:
    optimisation_request_resolver.py

Purpose:
    Resolves high-level optimisation requests into legal
    optimiser candidate armies.

Created:
    DEV-052 – Legal Composition Enumeration
"""

from army_profile_resolver import resolve_army_profiles
from composition_enumerator import (
    enumerate_legal_quantity_candidates,
)
from composition_resolver import (
    build_legal_multi_group_candidates,
)
from optimisation_request import OptimisationRequest
from optimiser_candidate import OptimiserCandidate
from profiles import Profile


def build_request_candidates(
    request: OptimisationRequest,
    profiles: list[Profile],
) -> tuple[OptimiserCandidate, ...]:
    """
    Builds legal candidates for an optimisation request.

    Requests with a composition specification generate
    constrained candidates.

    Requests without a composition specification generate
    unrestricted candidates from the army's complete profile
    pool.

    Optimisation goals are deliberately not evaluated here.
    They belong to the objective-function layer.
    """

    if request.composition_spec is not None:
        return build_legal_multi_group_candidates(
            spec=request.composition_spec,
            profiles=profiles,
            points_limit=request.points_limit,
        )

    army_profiles = resolve_army_profiles(
        army=request.army,
        profiles=profiles,
    )

    return enumerate_legal_quantity_candidates(
        profiles=army_profiles,
        points_limit=request.points_limit,
    )

