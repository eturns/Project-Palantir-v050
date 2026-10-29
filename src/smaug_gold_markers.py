"""DEV-077-SMAUG-D5B — immutable Gold Marker lifecycle.

Edward Turns (Project Lead)
Source: MESBG Armies of the Hobbit (2024), Desolator of the North.
This module does not change army scores or simulate unprovided battlefield actions.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from enum import Enum


class GoldMarkerLocation(Enum):
    CARRIED = 'carried'
    DROPPED = 'dropped'
    RECOVERED = 'recovered'


@dataclass(frozen=True)
class GoldMarker:
    id: str
    location: GoldMarkerLocation
    carrier_id: str | None = None

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError('Gold marker id must be a nonblank string')
        if not isinstance(self.location, GoldMarkerLocation):
            raise TypeError('location must be GoldMarkerLocation')
        if self.location is GoldMarkerLocation.CARRIED:
            if not isinstance(self.carrier_id, str) or not self.carrier_id.strip():
                raise ValueError('Carried marker must have a carrier id')
        elif self.carrier_id is not None:
            raise ValueError('Dropped/recovered markers cannot have a carrier')


@dataclass(frozen=True)
class SmaugGoldState:
    markers: tuple[GoldMarker, ...]
    smaug_model_id: str

    def __post_init__(self):
        if not isinstance(self.smaug_model_id, str) or not self.smaug_model_id.strip():
            raise ValueError('Smaug model id must be a nonblank string')
        if not isinstance(self.markers, tuple) or len(self.markers) != 3 or not all(
            isinstance(m, GoldMarker) for m in self.markers
        ):
            raise ValueError('Gold state requires exactly three GoldMarkers')
        if len({m.id for m in self.markers}) != 3:
            raise ValueError('Gold marker IDs must be unique')
        if any(m.location is GoldMarkerLocation.CARRIED and
               m.carrier_id == self.smaug_model_id for m in self.markers):
            raise ValueError('Smaug immediately recovers, never carries, a gold marker')

    def marker(self, marker_id: str) -> GoldMarker:
        for item in self.markers:
            if item.id == marker_id:
                return item
        raise ValueError(f'Unknown gold marker: {marker_id!r}')

    def _updated(self, marker_id: str, replacement: GoldMarker) -> 'SmaugGoldState':
        self.marker(marker_id)
        return replace(self, markers=tuple(
            replacement if m.id == marker_id else m for m in self.markers
        ))

    @property
    def recovered_count(self) -> int:
        return sum(m.location is GoldMarkerLocation.RECOVERED for m in self.markers)

    @property
    def enemy_carrier_ids(self) -> frozenset[str]:
        """These carriers qualify as objective carriers for Lust for Gold."""
        return frozenset(m.carrier_id for m in self.markers
                         if m.location is GoldMarkerLocation.CARRIED)


def deploy_gold_markers(enemy_model_ids: tuple[str, str, str], *,
                        smaug_model_id: str) -> SmaugGoldState:
    """Called after both armies deploy; three *different* enemy models selected."""
    if not isinstance(enemy_model_ids, tuple) or len(enemy_model_ids) != 3 or any(
        not isinstance(x, str) or not x.strip() for x in enemy_model_ids
    ):
        raise ValueError('Deployment requires exactly three nonblank enemy model IDs')
    if len(set(enemy_model_ids)) != 3 or smaug_model_id in enemy_model_ids:
        raise ValueError('Initial gold marker carriers must be three distinct enemies')
    return SmaugGoldState(tuple(GoldMarker(f'GOLD_{i}', GoldMarkerLocation.CARRIED, carrier)
                                for i, carrier in enumerate(enemy_model_ids, 1)),
                          smaug_model_id)


def kill_gold_carrier(state: SmaugGoldState, *, marker_id: str,
                      slain_model_id: str, killed_by_smaug_in_combat: bool) -> SmaugGoldState:
    """Combat kill by Smaug recovers; all other deaths drop the Light Object."""
    if type(killed_by_smaug_in_combat) is not bool:
        raise TypeError('killed_by_smaug_in_combat must be bool')
    marker = state.marker(marker_id)
    if marker.location is not GoldMarkerLocation.CARRIED or marker.carrier_id != slain_model_id:
        raise ValueError('Slain model does not carry the specified marker')
    destination = (GoldMarkerLocation.RECOVERED if killed_by_smaug_in_combat
                   else GoldMarkerLocation.DROPPED)
    return state._updated(marker_id, GoldMarker(marker_id, destination))


def pick_up_gold_marker(state: SmaugGoldState, *, marker_id: str,
                        picking_model_id: str) -> SmaugGoldState:
    """Pickup requires an independently established legal Light Object pickup."""
    marker = state.marker(marker_id)
    if marker.location is not GoldMarkerLocation.DROPPED:
        raise ValueError('Only a dropped gold marker may be picked up')
    if not isinstance(picking_model_id, str) or not picking_model_id.strip():
        raise ValueError('Picking model id must be nonblank')
    if picking_model_id == state.smaug_model_id:
        return state._updated(marker_id, GoldMarker(marker_id, GoldMarkerLocation.RECOVERED))
    return state._updated(marker_id, GoldMarker(marker_id, GoldMarkerLocation.CARRIED,
                                                picking_model_id))


def pass_gold_marker(*args, **kwargs) -> None:
    """Gold Markers cannot voluntarily be passed to another model."""
    raise ValueError('Gold Markers can never be passed to another model')
