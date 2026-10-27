"""DEV-077-TT-D3A: baseline Campfire army rule (2024 Armies of the Hobbit, p.158).

Explicit evidence only. The caller supplies deployment and model-to-fire distance;
this module does not infer coordinates, evaluate banner rerolls, or alter scoring.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

TROLL_PROFILE_IDS = frozenset({'TT_BILL', 'TT_BERT', 'TT_TOM'})
CAMPFIRE_BASE_MM = 80
BASE_RADIUS_INCHES = 6.0


@dataclass(frozen=True)
class CampfirePlacement:
    both_armies_deployed: bool
    on_battlefield: bool
    outside_opponent_deployment_zone: bool
    flat_on_battlefield: bool

    def __post_init__(self) -> None:
        for key in ('both_armies_deployed', 'on_battlefield',
                    'outside_opponent_deployment_zone', 'flat_on_battlefield'):
            if not isinstance(getattr(self, key), bool):
                raise TypeError(f'{key} must be bool')


@dataclass(frozen=True)
class CampfireEffects:
    status: str
    within_range: bool | None
    banner_applies: bool
    resistant_to_magic: bool
    courage_test_modifier: int
    campfire_base_mm: int = CAMPFIRE_BASE_MM
    reason: str | None = None


def campfire_placement_permitted(placement: CampfirePlacement) -> bool:
    """Requires completed deployment, legal zone, battlefield, flat placement."""
    if not isinstance(placement, CampfirePlacement):
        raise TypeError('placement must be CampfirePlacement')
    return all((placement.both_armies_deployed, placement.on_battlefield,
                placement.outside_opponent_deployment_zone,
                placement.flat_on_battlefield))


def evaluate_campfire_effects(
    profile_id: str,
    *,
    campfire_placed: bool | None,
    distance_inches: float | None = None,
    range_inches: float = BASE_RADIUS_INCHES,
) -> CampfireEffects:
    """Evaluate a friendly Troll's proximity benefits at an observed distance.

    range_inches allows a *later* purchased-upgrade integration (18 inches),
    but this module does not infer that upgrade from the army list.
    """
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError('profile_id must be a nonempty string')
    if campfire_placed is not None and not isinstance(campfire_placed, bool):
        raise TypeError('campfire_placed must be bool or None')
    for field, value in (('distance_inches', distance_inches), ('range_inches', range_inches)):
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                  or not isfinite(value) or value < 0):
            raise ValueError(f'{field} must be finite and nonnegative')
    if range_inches == 0:
        raise ValueError('range_inches must be positive')

    empty = dict(banner_applies=False, resistant_to_magic=False, courage_test_modifier=0)
    if profile_id not in TROLL_PROFILE_IDS:
        return CampfireEffects('not_applicable', False, **empty, reason='not_three_trolls_profile')
    if campfire_placed is None:
        return CampfireEffects('not_evaluated', None, **empty, reason='campfire_presence_unknown')
    if not campfire_placed:
        return CampfireEffects('evaluated', False, **empty, reason='campfire_not_placed')
    if distance_inches is None:
        return CampfireEffects('not_evaluated', None, **empty, reason='distance_unknown')
    in_range = distance_inches <= range_inches
    return CampfireEffects(
        'evaluated', in_range,
        banner_applies=in_range,
        resistant_to_magic=in_range,
        courage_test_modifier=1 if in_range else 0,
    )
