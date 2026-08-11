"""
Project Palantír
================

File:
    composition_resolver.py

Purpose:
    Resolves composition specifications against canonical
    Profile objects.

Created:
    DEV-052 – Legal Composition Enumeration
"""
from composition_enumerator import (
    build_candidate,
    enumerate_repeated_selections,
    filter_legal_candidates,
)
from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)
from profiles import Profile
from itertools import product

def resolve_fixed_profiles(
    spec: CompositionSpec,
    profiles: list[Profile],
) -> tuple[Profile, ...]:
    """
    Resolves fixed profile IDs and quantities into canonical
    Profile objects.
    """

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    resolved = []

    for profile_id, quantity in spec.fixed_profiles:
        resolved.extend(
            profiles_by_id[profile_id]
            for _ in range(quantity)
        )

    return tuple(resolved)

def resolve_selection_group(
    group: CompositionSelectionGroup,
    profiles: list[Profile],
) -> tuple[Profile, ...]:
    """
    Resolves a selection group's profile IDs into canonical
    Profile objects.
    """

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    return tuple(
        profiles_by_id[profile_id]
        for profile_id in group.profile_ids
    )

def enumerate_group_selections(
    group: CompositionSelectionGroup,
    profiles: list[Profile],
) -> tuple[tuple[Profile, ...], ...]:
    """
    Resolves a selection group and generates every unique
    repeated selection of the requested size.
    """

    resolved_profiles = resolve_selection_group(
        group=group,
        profiles=profiles,
    )

    return enumerate_repeated_selections(
        items=resolved_profiles,
        selection_size=group.selection_size,
    )

def build_single_group_candidates(
    spec: CompositionSpec,
    profiles: list[Profile],
):
    """
    Builds optimiser candidates from fixed profiles and one
    selectable composition group.
    """

    fixed_profiles = resolve_fixed_profiles(
        spec=spec,
        profiles=profiles,
    )

    if len(spec.selection_groups) != 1:
        raise ValueError(
            "build_single_group_candidates requires exactly one "
            "selection group."
        )

    selections = enumerate_group_selections(
        group=spec.selection_groups[0],
        profiles=profiles,
    )

    return tuple(
        build_candidate(
            fixed_profiles + selection
        )
        for selection in selections
    )

def build_multi_group_candidates(
    spec: CompositionSpec,
    profiles: list[Profile],
):
    """
    Builds optimiser candidates from fixed profiles and
    multiple selectable composition groups.
    """

    fixed_profiles = resolve_fixed_profiles(
        spec=spec,
        profiles=profiles,
    )

    group_selections = tuple(
        enumerate_group_selections(
            group=group,
            profiles=profiles,
        )
        for group in spec.selection_groups
    )

    return tuple(
        build_candidate(
            fixed_profiles
            + tuple(
                profile
                for selection in selection_combination
                for profile in selection
            )
        )
        for selection_combination in product(*group_selections)
    )

def build_legal_multi_group_candidates(
    spec: CompositionSpec,
    profiles: list[Profile],
    points_limit: int,
):
    """
    Builds multi-group optimiser candidates and retains only
    armies that satisfy existing Army validation.
    """

    candidates = build_multi_group_candidates(
        spec=spec,
        profiles=profiles,
    )

    return filter_legal_candidates(
        candidates=candidates,
        points_limit=points_limit,
    )