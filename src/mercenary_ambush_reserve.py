"""DEV-077-GUN-C5-B1: Goblin Mercenary Ambush reserve eligibility and arrival choice.

This module deliberately does not place models on terrain, apply reinforcements,
or alter Activation/Move eligibility after arrival (C5-B2/B3).
"""
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

CAPTAIN = 'GOBLIN_MERCENARY_CAPTAIN'
MERCENARY = 'GOBLIN_MERCENARY'


class ArrivalDecisionOwner(Enum):
    CONTROLLING_PLAYER = 'controlling_player'
    OPPOSING_PLAYER = 'opposing_player'


@dataclass(frozen=True)
class AmbushReserve:
    """State for one warband; only eligible warbands may enter reserve."""
    warband_id: str
    in_reserve: bool = True
    arrived: bool = False

    def __post_init__(self):
        if not self.warband_id:
            raise ValueError('Warband ID is required.')
        if self.in_reserve and self.arrived:
            raise ValueError('A warband cannot be in reserve and arrived.')


def eligible_for_mercenary_ambush(leader_profile_id: str, member_profile_ids: Iterable[str]) -> bool:
    """Require Mercenary Captain leader and only Mercenary warrior members."""
    return leader_profile_id == CAPTAIN and all(
        profile_id == MERCENARY for profile_id in member_profile_ids
    )


def eligible_warbands_from_definition(definition) -> tuple[str, ...]:
    """Inspect ArmyDefinition entries; incomplete/ambiguous warbands fail closed."""
    by_warband: dict[str, list] = {}
    for entry in definition.entries:
        if entry.warband_id is not None:
            by_warband.setdefault(entry.warband_id, []).append(entry)
    eligible = []
    for warband_id, entries in by_warband.items():
        leaders = [entry for entry in entries if entry.is_warband_leader]
        if len(leaders) != 1:
            continue
        if eligible_for_mercenary_ambush(
            leaders[0].profile_id,
            (entry.profile_id for entry in entries if not entry.is_warband_leader),
        ):
            eligible.append(warband_id)
    return tuple(eligible)


def intelligence_test_passed(target: str, dice: tuple[int, int]) -> bool:
    """Resolve a standard 2D6 Intelligence test against an X+ target."""
    if not isinstance(target, str) or not target.endswith('+'):
        raise ValueError('Intelligence target must be an X+ string.')
    try:
        required = int(target[:-1])
    except ValueError as exc:
        raise ValueError('Intelligence target must be an X+ string.') from exc
    if not 2 <= required <= 12:
        raise ValueError('Intelligence target must be within 2+ to 12+.')
    if (not isinstance(dice, tuple) or len(dice) != 2
            or any(type(die) is not int or not 1 <= die <= 6 for die in dice)):
        raise ValueError('Intelligence test requires two natural D6 results.')
    return sum(dice) >= required


def resolve_ambush_arrival_decision(
    reserve: AmbushReserve,
    *,
    turn: int,
    end_of_controlling_activation: bool,
    intelligence_target: str,
    dice: tuple[int, int],
) -> ArrivalDecisionOwner | None:
    """Returns who may choose whether the reserve arrives, not actual arrival."""
    if type(turn) is not int or turn < 1:
        raise ValueError('Turn must be a positive integer.')
    if type(end_of_controlling_activation) is not bool:
        raise TypeError('Phase indicator must be boolean.')
    if not reserve.in_reserve or reserve.arrived or turn < 2 or not end_of_controlling_activation:
        return None
    return (ArrivalDecisionOwner.CONTROLLING_PLAYER
            if intelligence_test_passed(intelligence_target, dice)
            else ArrivalDecisionOwner.OPPOSING_PLAYER)
