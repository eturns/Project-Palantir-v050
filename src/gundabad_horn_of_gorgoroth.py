"""DEV-078-AoG-D1: Horn of Gorgoroth once-per-game state machine.

Author: Edward Turns (Project Lead).

No battlefield positions, general survival, Priority, or enemy identity are
inferred. The caller supplies these observed facts. Effect lasts one turn.
"""
from dataclasses import dataclass
from fractions import Fraction

ARMY_LIST_ID = 'GUNDABAD'
RULE_ID = 'GUNDABAD_HORN_OF_GORGOROTH'


@dataclass(frozen=True)
class HornState:
    turn: int = 1
    used: bool = False
    active_turn: int | None = None

    def __post_init__(self):
        if type(self.turn) is not int or self.turn < 1:
            raise ValueError('turn must be a positive integer')
        if type(self.used) is not bool:
            raise TypeError('used must be boolean')
        if self.active_turn is not None:
            if type(self.active_turn) is not int or self.active_turn < 1:
                raise ValueError('active_turn must be a positive integer')
            if not self.used or self.active_turn > self.turn:
                raise ValueError('active_turn inconsistent with Horn state')


@dataclass(frozen=True)
class HornActivation:
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    general_alive: bool
    general_on_battlefield: bool
    priority_determined: bool
    activate: bool


@dataclass(frozen=True)
class HornActivationResult:
    state: HornState
    activated: bool
    status: str


def activate_horn(state: HornState, request: HornActivation) -> HornActivationResult:
    if not isinstance(state, HornState) or not isinstance(request, HornActivation):
        raise TypeError('HornState and HornActivation required')
    for name in ('general_alive', 'general_on_battlefield', 'priority_determined', 'activate'):
        if type(getattr(request, name)) is not bool:
            raise TypeError(f'{name} must be boolean')
    if not isinstance(request.active_army_rule_ids, tuple) or any(
        not isinstance(x, str) for x in request.active_army_rule_ids
    ):
        raise TypeError('active_army_rule_ids must be strings')
    if not request.activate:
        return HornActivationResult(state, False, 'not_declared')
    if request.army_list_id != ARMY_LIST_ID or RULE_ID not in request.active_army_rule_ids:
        return HornActivationResult(state, False, 'not_entitled')
    if state.used:
        return HornActivationResult(state, False, 'already_used')
    if not request.priority_determined:
        return HornActivationResult(state, False, 'priority_not_determined')
    if not request.general_alive or not request.general_on_battlefield:
        return HornActivationResult(state, False, 'general_unavailable')
    new = HornState(state.turn, True, state.turn)
    return HornActivationResult(new, True, 'activated')


def advance_turn(state: HornState) -> HornState:
    if not isinstance(state, HornState):
        raise TypeError('HornState required')
    return HornState(state.turn + 1, state.used, state.active_turn)


def horn_active(state: HornState) -> bool:
    if not isinstance(state, HornState):
        raise TypeError('HornState required')
    return state.used and state.active_turn == state.turn


def horn_courage_modifier(state: HornState, *, friendly_gundabad: bool = False,
                          enemy: bool = False, existing_enemy_penalty: int = 0) -> int:
    """Return Horn-related modifier; enemy penalty is non-cumulative.

    existing_enemy_penalty is the already applicable (non-positive) penalty
    from a similar effect. The returned enemy value is the effective combined
    *penalty*, so it can be supplied to the standard Courage context. Bonuses
    from unrelated sources must be handled separately by the caller.
    """
    if type(friendly_gundabad) is not bool or type(enemy) is not bool:
        raise TypeError('Model relationships must be boolean')
    if friendly_gundabad and enemy:
        raise ValueError('Model cannot be friendly Gundabad and enemy')
    if type(existing_enemy_penalty) is not int or existing_enemy_penalty > 0:
        raise ValueError('existing_enemy_penalty must be a non-positive integer')
    if friendly_gundabad:
        return 2 if horn_active(state) else 0
    if enemy:
        return min(existing_enemy_penalty, -2) if horn_active(state) else existing_enemy_penalty
    return 0


def courage_probability_with_horn(combatant, state: HornState, *,
                                   friendly_gundabad=False, enemy=False,
                                   existing_enemy_penalty=0, other_roll_modifier=0):
    """Delegate 2D6 arithmetic to Palantir's canonical Courage engine."""
    from courage_test import (CourageTestContext, calculate_courage_test_success_probability)
    if type(other_roll_modifier) is not int:
        raise TypeError('other_roll_modifier must be integer')
    effect = horn_courage_modifier(state, friendly_gundabad=friendly_gundabad,
                                  enemy=enemy, existing_enemy_penalty=existing_enemy_penalty)
    return calculate_courage_test_success_probability(
        combatant, CourageTestContext(roll_modifier=effect + other_roll_modifier)
    )
