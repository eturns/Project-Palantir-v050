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

from composition_enumerator import (
    enumerate_legal_quantity_candidates,
)
from composition_resolver import (
    build_legal_multi_group_candidates,
)
from optimisation_request import OptimisationRequest
from optimiser_candidate import OptimiserCandidate


def build_request_candidates(
    request: OptimisationRequest,
) -> tuple[OptimiserCandidate, ...]:
    """
    Builds legal candidates for an optimisation request.

    ArmyList membership is the authoritative profile pool.

    Requests with a composition specification generate
    constrained candidates from that pool.

    Requests without a composition specification generate
    unrestricted candidates from the ArmyList's complete
    profile pool.

    Optimisation goals are deliberately not evaluated here.
    They belong to the objective-function layer.
    """

    army_profiles = tuple(
        request.army_list.profiles
    )

    if request.composition_spec is not None:
        return build_legal_multi_group_candidates(
            spec=request.composition_spec,
            profiles=army_profiles,
            points_limit=request.points_limit,
        )

    return enumerate_legal_quantity_candidates(
        profiles=army_profiles,
        points_limit=request.points_limit,
    )