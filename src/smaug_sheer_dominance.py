"""DEV-077-SMAUG-D2: source-gated Smaug objective dominance evidence.
Edward Turns (Project Lead). Diagnostic-only, no score mutations.
"""
from dataclasses import dataclass
from math import isfinite
from objective_control_override import ObjectiveControlOverride

SHEER_DOMINANCE_RULE_ID = 'SHEER_DOMINANCE'


@dataclass(frozen=True)
class SheerDominanceEvidence:
    rule_present: bool
    in_objective_range: bool | None
    override: ObjectiveControlOverride | None
    status: str


def evaluate_smaug_sheer_dominance(*, profile_id: str,
                                     rule_ids: frozenset[str],
                                     distance_to_objective_inches: float | None,
                                     objective_range_inches: float | None) -> SheerDominanceEvidence:
    """Caller must supply the scenario's actual objective range.

    None range/distance deliberately produces unknown, not assumed control.
    Only Smaug with the assigned canonical rule may activate the override.
    """
    if profile_id != 'SMAUG':
        raise ValueError('Sheer Dominance adapter requires Smaug')
    if not isinstance(rule_ids, frozenset) or not all(isinstance(x,str) for x in rule_ids):
        raise TypeError('rule_ids must be a frozenset of strings')
    for name, value in [('distance_to_objective_inches',distance_to_objective_inches),
                        ('objective_range_inches',objective_range_inches)]:
        if value is not None:
            if isinstance(value,bool) or not isinstance(value,(float,int)):
                raise TypeError(name+' must be numeric or None')
            if not isfinite(value) or value < 0:
                raise ValueError(name+' must be finite and nonnegative')
    present = SHEER_DOMINANCE_RULE_ID in rule_ids
    if not present:
        return SheerDominanceEvidence(False,None,ObjectiveControlOverride.NONE,'rule_not_assigned')
    if distance_to_objective_inches is None or objective_range_inches is None:
        return SheerDominanceEvidence(True,None,None,'conditional_not_evaluated')
    near = distance_to_objective_inches <= objective_range_inches
    return SheerDominanceEvidence(True,near,
       ObjectiveControlOverride.SHEER_DOMINANCE if near else ObjectiveControlOverride.NONE,
       'evaluated')
