"""DEV-077-TT-D2A: Bill's Mince 'em Fine Brutal Power Attack.

Source: MESBG Armies of the Hobbit (2024), Bill the Troll, p. 140.
This is a conditional combat resolver, not an unconditional offence bonus.
"""
from fractions import Fraction

BILL_PROFILE_ID = 'TT_BILL'


def mince_em_fine_wounds(*, bill_strength: int, target_strength: int,
                         bill_roll: int, target_roll: int) -> int:
    """After a won Duel, wounds equal Bill's positive D6+S margin."""
    for label, number in (("bill_strength", bill_strength),
                          ("target_strength", target_strength)):
        if type(number) is not int or not 1 <= number <= 10:
            raise ValueError(f'{label} must be an integer between 1 and 10')
    for label, number in (("bill_roll", bill_roll),
                          ("target_roll", target_roll)):
        if type(number) is not int or not 1 <= number <= 6:
            raise ValueError(f'{label} must be a D6 result (1..6)')
    return max(0, bill_strength + bill_roll - target_strength - target_roll)


def mince_em_fine_distribution(*, bill_strength: int,
                                 target_strength: int) -> dict[int, Fraction]:
    """Exact 36-outcome distribution conditional on choosing this attack."""
    outcome_counts: dict[int, int] = {}
    for bill_roll in range(1, 7):
        for target_roll in range(1, 7):
            wounds = mince_em_fine_wounds(
                bill_strength=bill_strength, target_strength=target_strength,
                bill_roll=bill_roll, target_roll=target_roll)
            outcome_counts[wounds] = outcome_counts.get(wounds, 0) + 1
    return {wounds: Fraction(count, 36)
            for wounds, count in sorted(outcome_counts.items())}


def mince_em_fine_expected_wounds(*, bill_strength: int,
                                    target_strength: int) -> Fraction:
    """Expected unsaved wounds before Fate/ignore-wound effects, conditional on a won Duel."""
    return sum((w * p for w, p in mince_em_fine_distribution(
        bill_strength=bill_strength, target_strength=target_strength).items()),
        Fraction(0, 1))
