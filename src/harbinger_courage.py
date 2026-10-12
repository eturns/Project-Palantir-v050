"""DEV-077S-I2-E-B2: contextual Harbinger of Evil Courage modifier.

This module provides a rule-grounded modifier, not a capability score.
Caller supplies *enemy* influences and measured distances. Affected models
with Harbinger of Evil are immune to enemy Harbinger modifiers.
"""

from dataclasses import dataclass
from math import isfinite

from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from effective_special_rule_ids import get_effective_special_rule_ids

Combatant = ConfiguredProfile | FieldedModelFormState
RULE_ID = "HARBINGER_OF_EVIL"


@dataclass(frozen=True)
class HarbingerInfluence:
    provider: Combatant
    distance_inches: float

    def __post_init__(self) -> None:
        if (isinstance(self.distance_inches, bool)
                or not isinstance(self.distance_inches, (int, float))
                or not isfinite(self.distance_inches)
                or self.distance_inches < 0):
            raise ValueError("Harbinger distance must be a finite non-negative number.")


def _active_profile(model: Combatant) -> ConfiguredProfile:
    if isinstance(model, FieldedModelFormState):
        return model.active_configured_profile
    return model


def _harbinger_range_inches(model: Combatant) -> float | None:
    if RULE_ID not in get_effective_special_rule_ids(model):
        return None
    configured = _active_profile(model)
    for assignment in configured.effective_special_rules:
        if assignment.rule.id != RULE_ID:
            continue
        value = assignment.parameter
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Harbinger of Evil requires a numeric range parameter.")
        if not isfinite(value) or value <= 0:
            raise ValueError("Harbinger of Evil range must be positive and finite.")
        return float(value)
    # A runtime-granted rule may need a separate, state-aware range resolver.
    # Do not guess its range from an unrelated static profile.
    raise ValueError("Harbinger of Evil is active without a configured range parameter.")


def calculate_harbinger_roll_modifier(
    target: Combatant,
    influences: tuple[HarbingerInfluence, ...] | list[HarbingerInfluence],
) -> int:
    """Return 0 or -1 from enemy Harbinger sources (non-stacking).

    The caller must supply only enemy sources; allegiance is not inferred.
    Other non-stacking Courage penalties are deliberately out of scope.
    """
    if RULE_ID in get_effective_special_rule_ids(target):
        return 0
    for influence in influences:
        radius = _harbinger_range_inches(influence.provider)
        if radius is not None and influence.distance_inches <= radius:
            return -1
    return 0
