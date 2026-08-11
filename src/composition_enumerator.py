"""
Project Palantír
================

File:
    composition_enumerator.py

Purpose:
    Provides deterministic enumeration of composition selections.

Created:
    DEV-052 – Legal Composition Enumeration
"""

from itertools import (
    combinations,
    combinations_with_replacement,
)
from army import Army
from optimiser_candidate import OptimiserCandidate
from profiles import Profile

def enumerate_selections(
    items: tuple,
    selection_size: int,
) -> tuple[tuple, ...]:
    """
    Returns all unique fixed-size selections from the supplied items.

    Selection order follows the order of the supplied item collection.
    """

    return tuple(
        combinations(
            items,
            selection_size,
        )
    )

def enumerate_repeated_selections(
    items: tuple,
    selection_size: int,
) -> tuple[tuple, ...]:
    """
    Returns all unique fixed-size selections where items
    may appear more than once.

    Selection order follows the order of the supplied
    item collection.
    """

    return tuple(
        combinations_with_replacement(
            items,
            selection_size,
        )
    )

def build_candidate(
    selection: tuple[Profile, ...],
) -> OptimiserCandidate:
    """
    Builds an optimiser candidate from a profile selection.

    Repeated profiles are grouped into one ArmyEntry
    with the appropriate quantity.
    """

    army = Army()

    quantities = {}

    for profile in selection:
        quantities[profile.id] = (
            profile,
            quantities.get(
                profile.id,
                (
                    profile,
                    0,
                ),
            )[1] + 1,
        )

    for profile, quantity in quantities.values():
        army.add_profile(
            profile,
            quantity=quantity,
        )

    return OptimiserCandidate(
        army=army,
    )

def filter_legal_candidates(
    candidates: tuple[OptimiserCandidate, ...],
    points_limit: int,
) -> tuple[OptimiserCandidate, ...]:
    """
    Returns only candidates that satisfy Army validation.
    """

    return tuple(
        candidate
        for candidate in candidates
        if candidate.army.validate(points_limit) == []
    )

def enumerate_profile_quantities(
    profile: Profile,
    points_limit: int,
) -> tuple[int, ...]:
    """
    Returns every quantity of a profile that could fit
    within the supplied points limit.

    max_in_army == 0 represents no explicit copy limit.
    """

    points_maximum = points_limit // profile.points

    if profile.max_in_army == 0:
        maximum_quantity = points_maximum
    else:
        maximum_quantity = min(
            profile.max_in_army,
            points_maximum,
        )

    return tuple(
        range(maximum_quantity + 1)
    )

def enumerate_quantity_candidates(
    profiles: tuple[Profile, ...],
    points_limit: int,
) -> tuple[OptimiserCandidate, ...]:
    """
    Generates candidate armies from every possible profile
    quantity combination permitted by profile limits and the
    supplied points limit.

    Branches that exceed the points limit are pruned before
    complete candidate armies are constructed.

    The completely empty army is omitted.
    """

    candidates = []

    def build_next(
        profile_index: int,
        selected: tuple[tuple[Profile, int], ...],
        running_points: int,
    ) -> None:
        if profile_index == len(profiles):
            if not selected:
                return

            army = Army()

            for profile, quantity in selected:
                army.add_profile(
                    profile,
                    quantity=quantity,
                )

            candidates.append(
                OptimiserCandidate(
                    army=army,
                )
            )

            return

        profile = profiles[profile_index]

        quantities = enumerate_profile_quantities(
            profile=profile,
            points_limit=points_limit,
        )

        for quantity in quantities:
            new_points = (
                running_points
                + profile.points * quantity
            )

            if new_points > points_limit:
                break

            if quantity == 0:
                new_selected = selected
            else:
                new_selected = selected + (
                    (profile, quantity),
                )

            build_next(
                profile_index=profile_index + 1,
                selected=new_selected,
                running_points=new_points,
            )

    build_next(
        profile_index=0,
        selected=(),
        running_points=0,
    )

    return tuple(candidates)

def enumerate_legal_quantity_candidates(
    profiles: tuple[Profile, ...],
    points_limit: int,
) -> tuple[OptimiserCandidate, ...]:
    """
    Generates unrestricted quantity candidates and retains
    only armies that satisfy existing Army validation.
    """

    candidates = enumerate_quantity_candidates(
        profiles=profiles,
        points_limit=points_limit,
    )

    return filter_legal_candidates(
        candidates=candidates,
        points_limit=points_limit,
    )