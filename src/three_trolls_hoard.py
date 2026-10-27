"""DEV-077-TT-D3B: purchased-upgrade activation contract (2024 Hobbit p.158).

Purchase truth comes from ArmyDefinition.army_upgrade_names and purchases.
This is an explicit diagnostic contract, NOT automatic battlefield resolution.
"""
from __future__ import annotations

from dataclasses import dataclass

from three_trolls_upgrades import (
    THREE_TROLLS_ARMY_LIST_ID,
    THREE_TROLLS_UPGRADE_NAMES,
    THREE_TROLLS_UPGRADE_COST,
)


@dataclass(frozen=True)
class HoardUpgrade:
    name: str
    purchase_id: str
    points: int
    activated: bool
    effect_key: str
    evidence_status: str


@dataclass(frozen=True)
class HoardEvidence:
    army_list_id: str
    active_upgrades: tuple[str, ...]
    purchase_points: int
    upgrades: tuple[HoardUpgrade, ...]
    campfire_range_inches: float

    def has(self, name: str) -> bool:
        if name not in THREE_TROLLS_UPGRADE_NAMES:
            raise ValueError(f'Unknown Three Trolls upgrade: {name!r}')
        return name in self.active_upgrades


_EFFECT_KEYS = (
    'heroic_resources_start_at_3',
    'ignore_wound_on_natural_6',
    'campfire_18_inch_and_banner_vp_if_uncontested',
    'four_attacks_when_charging',
    'throwing_stones_and_hurl_distance_reroll',
    'objective_dominance_with_conflict_rule',
    'heroic_strike_and_reaction_roll',
    'four_livestock_healing_markers',
    'optional_night_and_cave_dweller',
    'standing_not_trapped_and_trapped_target_wound_reroll',
    'natural_one_wound_reroll_for_strikes',
    'one_stash_marker_per_troll_with_objective_control',
)


def build_hoard_evidence(definition) -> HoardEvidence | None:
    """Validate the *actual* purchase ledger and expose effects only if paid for.

    Battlefield effects remain conditional: an activation entry isn't a
    claim that a particular model, target or scenario satisfies conditions.
    """
    if definition.army_list_id != THREE_TROLLS_ARMY_LIST_ID:
        return None
    names = tuple(definition.army_upgrade_names)
    if len(names) != len(set(names)):
        raise ValueError('Duplicate Three Trolls upgrade')
    if any(name not in THREE_TROLLS_UPGRADE_NAMES for name in names):
        raise ValueError('Unknown Three Trolls upgrade')
    purchases = tuple(definition.purchases)
    actual = [p for p in purchases if str(p.id).startswith('TT_UPGRADE:')]
    wanted_ids = {'TT_UPGRADE:' + name for name in names}
    if len(actual) != len(wanted_ids) or {p.id for p in actual} != wanted_ids:
        raise ValueError('Three Trolls selected upgrades do not match purchases')
    for purchase in actual:
        if (purchase.points != THREE_TROLLS_UPGRADE_COST or purchase.quantity != 1
                or purchase.warband_id is not None):
            raise ValueError('Three Trolls upgrade must be a single 50-point army purchase')
    selected = frozenset(names)
    upgrades = tuple(
        HoardUpgrade(
            name=name,
            purchase_id='TT_UPGRADE:' + name,
            points=THREE_TROLLS_UPGRADE_COST if name in selected else 0,
            activated=name in selected,
            effect_key=_EFFECT_KEYS[index],
            evidence_status='conditional_not_evaluated' if name in selected else 'not_purchased',
        )
        for index, name in enumerate(THREE_TROLLS_UPGRADE_NAMES)
    )
    return HoardEvidence(
        army_list_id=THREE_TROLLS_ARMY_LIST_ID,
        active_upgrades=names,
        purchase_points=50 * len(names),
        upgrades=upgrades,
        campfire_range_inches=18.0 if 'Nothing like a warm fire' in selected else 6.0,
    )
