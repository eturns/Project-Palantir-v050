"""
Project Palantír
================

File:
    composition_spec.py

Purpose:
    Defines explicit composition assumptions used to
    generate optimiser candidate armies.

Created:
    DEV-052 – Legal Composition Enumeration
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CompositionSelectionGroup:
    """
    Defines a selectable profile pool and the number of
    models to choose from that pool.
    """

    profile_ids: tuple[str, ...]
    selection_size: int


@dataclass(frozen=True)
class CompositionSpec:
    """
    Defines the structure of an optimiser composition
    experiment.

    These are analysis assumptions and do not represent
    mandatory army-list rules.
    """

    fixed_profiles: tuple[tuple[str, int], ...] = ()
    selection_groups: tuple[CompositionSelectionGroup, ...] = ()