"""DEV-077-GUN-C3-A: Natural-six prevention of each suffered wound.

This is a post-ToWound prevention roll, independent of Fate.
It does not change the target's Defence or attacker wound probability.
"""
from fractions import Fraction

RULE_ID = 'OBLIVIOUS_TO_PAIN'


def prevention_probability(defender) -> Fraction:
    """Return per-wound prevention chance for a Profile/ConfiguredProfile."""
    assignments = getattr(defender, 'effective_special_rules', None)
    if assignments is None:
        assignments = getattr(defender, 'special_rules', ())
    if any(assignment.rule.id == RULE_ID for assignment in assignments):
        return Fraction(1, 6)
    return Fraction(0, 1)


def resolve_prevention_roll(defender, natural_roll: int) -> bool:
    """Resolve one physical D6; True means the wound is ignored."""
    if type(natural_roll) is not int or not 1 <= natural_roll <= 6:
        raise ValueError('Prevention roll must be an integer from 1 to 6.')
    return bool(prevention_probability(defender)) and natural_roll == 6
