"""DEV-077-SMAUG-C3A/E — exact single-shot Missing Scale diagnostic.

Scope: ordinary D6 shooting To Hit with an explicit modifier, independent
To Wound probability supplied from the canonical wound table. The rule triggers
ONLY on an original natural 6 which also hits, then successfully wounds.
Obstructions, Might-modified dice, rerolls, special immunity and alternative
attack procedures require separately declared contexts and are not inferred.
"""
from dataclasses import dataclass
from fractions import Fraction

from shooting_hit_probability import parse_shoot_value
from wound_table import get_wound_target
from wound_probability import get_wound_probability
from defensive_state import DefensiveState
from survival_probability import get_survival_probability_after_wounds


@dataclass(frozen=True)
class MissingScaleEvidence:
    ordinary_wound_probability: Fraction
    missing_scale_wound_probability: Fraction
    miss_or_no_wound_probability: Fraction
    expected_incoming_wounds: Fraction
    elimination_probability: Fraction
    status: str = "bounded_shot_no_obstructions_or_rerolls"


def calculate_missing_scale_evidence(
    *,
    shooter_shoot_value: str,
    missile_strength: int,
    smaug_defence: int = 9,
    to_hit_modifier: int = 0,
    smaug_state: DefensiveState | None = None,
    smaug_might_for_fate: int = 0,
) -> MissingScaleEvidence:
    """Probabilities for ONE eligible missile shot against Smaug.

    Normal successful hits cause 1 wound; a natural-six hit that wounds
    causes missile_strength wounds. Wound prevention is modelled for
    elimination, not for expected *incoming* wounds.
    """
    target = parse_shoot_value(shooter_shoot_value)
    if type(missile_strength) is not int or not 1 <= missile_strength <= 10:
        raise ValueError("missile_strength must be an integer from 1 to 10")
    if type(smaug_defence) is not int or not 1 <= smaug_defence <= 10:
        raise ValueError("smaug_defence must be an integer from 1 to 10")
    if type(to_hit_modifier) is not int:
        raise TypeError("to_hit_modifier must be an integer")
    if type(smaug_might_for_fate) is not int or smaug_might_for_fate < 0:
        raise ValueError("smaug_might_for_fate must be a nonnegative integer")
    if smaug_state is None:
        smaug_state = DefensiveState(20, 0, 0)
    if not isinstance(smaug_state, DefensiveState):
        raise TypeError("smaug_state must be DefensiveState")
    if smaug_state.remaining_will:
        raise ValueError("Will-as-Fate is not resolved by this diagnostic")
    if smaug_state.remaining_wounds == 0:
        raise ValueError("Smaug must be alive before this shooting attack")

    wound_prob = get_wound_probability(
        get_wound_target(strength=missile_strength, defence=smaug_defence)
    )
    # Enumerate actual original dice. A modified 6 on a natural 5 is
    # not Missing Scale. Natural 6 that fails a modified To Hit is not either.
    ordinary_hit_rolls = sum(
        (roll + to_hit_modifier >= target) and roll != 6
        for roll in range(1, 7)
    )
    critical_hit_rolls = int(6 + to_hit_modifier >= target)
    ordinary = Fraction(ordinary_hit_rolls, 6) * wound_prob
    special = Fraction(critical_hit_rolls, 6) * wound_prob
    none = Fraction(1) - ordinary - special
    expected = ordinary + special * missile_strength
    elimination = (
        ordinary * (
            1 - get_survival_probability_after_wounds(
                smaug_state, incoming_wounds=1,
                might_points=smaug_might_for_fate
            )
        )
        + special * (
            1 - get_survival_probability_after_wounds(
                smaug_state, incoming_wounds=missile_strength,
                might_points=smaug_might_for_fate
            )
        )
    )
    return MissingScaleEvidence(
        ordinary_wound_probability=ordinary,
        missing_scale_wound_probability=special,
        miss_or_no_wound_probability=none,
        expected_incoming_wounds=expected,
        elimination_probability=elimination,
    )
