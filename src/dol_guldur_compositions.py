"""
Project Palantír
================

File:
    dol_guldur_compositions.py

Purpose:
    Defines Dol Guldur-specific composition inputs for
    optimiser candidate generation.

Created:
    DEV-052 – Legal Composition Enumeration
"""
from composition_spec import (
    CompositionSelectionGroup,
    CompositionSpec,
)
from profiles import Profile

DOL_GULDUR_NECROMANCER_ID = "DG_NEC"
DOL_GULDUR_NAZGUL_IDS = (
    "DG_WK",
    "DG_KHM",
    "DG_DH",
    "DG_FS",
    "DG_LS",
    "DG_AK",
    "DG_SM",
)
DOL_GULDUR_SPIDER_IDS = (
    "DG_MGS",
    "DG_MHS",
)
DOL_GULDUR_PROFILE_IDS = (
    DOL_GULDUR_NECROMANCER_ID,
    *DOL_GULDUR_NAZGUL_IDS,
    *DOL_GULDUR_SPIDER_IDS,
)

def dol_guldur_nazgul_profiles(
    profiles: list[Profile],
) -> tuple[Profile, ...]:
    """
    Returns the canonical Dol Guldur Nazgûl profile pool.
    """

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    return tuple(
        profiles_by_id[profile_id]
        for profile_id in DOL_GULDUR_NAZGUL_IDS
    )

def dol_guldur_spider_profiles(
    profiles: list[Profile],
) -> tuple[Profile, ...]:
    """
    Returns the canonical Dol Guldur spider profile pool.
    """

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    return tuple(
        profiles_by_id[profile_id]
        for profile_id in DOL_GULDUR_SPIDER_IDS
    )

def dol_guldur_family_a_spec(
    profiles: list[Profile],
) -> CompositionSpec:
    """
    Returns the analysis composition for:

    Necromancer x1
    Nazgûl x6
    Spider x1
    """

    nazgul = dol_guldur_nazgul_profiles(
        profiles
    )

    spiders = dol_guldur_spider_profiles(
        profiles
    )

    return CompositionSpec(
        fixed_profiles=(
            (DOL_GULDUR_NECROMANCER_ID, 1),
        ),
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=tuple(
                    profile.id
                    for profile in nazgul
                ),
                selection_size=6,
            ),
            CompositionSelectionGroup(
                profile_ids=tuple(
                    profile.id
                    for profile in spiders
                ),
                selection_size=1,
            ),
        ),
    )

def dol_guldur_family_b_spec(
    profiles: list[Profile],
) -> CompositionSpec:
    """
    Returns the analysis composition for:

    Necromancer x1
    Nazgûl x5
    Spiders x5
    """

    nazgul = dol_guldur_nazgul_profiles(
        profiles
    )

    spiders = dol_guldur_spider_profiles(
        profiles
    )

    return CompositionSpec(
        fixed_profiles=(
            (DOL_GULDUR_NECROMANCER_ID, 1),
        ),
        selection_groups=(
            CompositionSelectionGroup(
                profile_ids=tuple(
                    profile.id
                    for profile in nazgul
                ),
                selection_size=5,
            ),
            CompositionSelectionGroup(
                profile_ids=tuple(
                    profile.id
                    for profile in spiders
                ),
                selection_size=5,
            ),
        ),
    )

def dol_guldur_profiles(
    profiles: list[Profile],
) -> tuple[Profile, ...]:
    """
    Returns the complete canonical Dol Guldur profile pool.
    """

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    return tuple(
        profiles_by_id[profile_id]
        for profile_id in DOL_GULDUR_PROFILE_IDS
    )