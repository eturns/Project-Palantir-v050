"""DEV-077-SMAUG-D5C: end-of-game Gold Marker VP award (unscored adapter).

Edward Turns (Project Lead)
Reads the immutable D5B gold state and reuses the generic VP modifier.
Does not alter army analysis, scenario forecasts or baseline metrics.
"""
from __future__ import annotations
from dataclasses import dataclass

from smaug_gold_markers import GoldMarkerLocation, SmaugGoldState
from victory_point_modifier import VictoryPointModifier, apply_victory_point_modifier

_GOLD_AWARD = VictoryPointModifier(amount=2, maximum_total=20)


@dataclass(frozen=True)
class SmaugGoldVictoryPointEvidence:
    smaug_points_before: int
    opponent_points_before: int
    smaug_bonus: int
    opponent_bonus: int
    smaug_points_after: int
    opponent_points_after: int
    recovered_markers: int
    enemy_carried_markers: int
    status: str = 'evaluated_end_of_game'


def calculate_smaug_gold_victory_points(
    state: SmaugGoldState, *, smaug_points: int, opponent_points: int
) -> SmaugGoldVictoryPointEvidence:
    """Evaluate official Gold Marker bonuses at the END of a game.

    If all recovered, Smaug gains +2. Otherwise, if any remain enemy-carried,
    the opponent gains +2. If all remaining markers are dropped, neither gains.
    Bonus points cannot raise either total beyond 20.
    """
    if not isinstance(state, SmaugGoldState):
        raise TypeError('state must be SmaugGoldState')
    for label, value in (('smaug_points', smaug_points), ('opponent_points', opponent_points)):
        if type(value) is not int or not 0 <= value <= 20:
            raise ValueError(f'{label} must be an integer from 0 to 20')

    recovered = sum(m.location is GoldMarkerLocation.RECOVERED for m in state.markers)
    carried = sum(m.location is GoldMarkerLocation.CARRIED for m in state.markers)
    smaug_earns = recovered == 3
    opponent_earns = not smaug_earns and carried > 0
    smaug_final = apply_victory_point_modifier(
        current_points=smaug_points, modifier=_GOLD_AWARD, condition_met=smaug_earns
    )
    opponent_final = apply_victory_point_modifier(
        current_points=opponent_points, modifier=_GOLD_AWARD, condition_met=opponent_earns
    )
    return SmaugGoldVictoryPointEvidence(
        smaug_points_before=smaug_points,
        opponent_points_before=opponent_points,
        smaug_bonus=smaug_final-smaug_points,
        opponent_bonus=opponent_final-opponent_points,
        smaug_points_after=smaug_final,
        opponent_points_after=opponent_final,
        recovered_markers=recovered,
        enemy_carried_markers=carried,
    )
