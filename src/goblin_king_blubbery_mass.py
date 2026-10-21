"""DEV-077-GT-C2A — The Goblin King's Blubbery Mass.

Wound is already inflicted; this models the special-rule prevention roll only.
Does not consume Fate or mutate a model, and requires attack provenance.
"""
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class BlubberyMassEvidence:
    applicable: bool
    prevention_probability: Fraction
    wound_remaining_probability: Fraction
    prevention_target: int | None


def blubbery_mass_evidence(*, magical_power: bool,
                           elven_combat_weapon: bool,
                           elven_missile_weapon: bool) -> BlubberyMassEvidence:
    """Return chance to prevent one inflicted wound (3+, or 4+ vs Elven missile).

    Magical Powers and Elven weapons used in Combat ignore Blubbery Mass.
    Conditions must be explicitly known; unknowns are not interpreted as False.
    """
    flags = (magical_power, elven_combat_weapon, elven_missile_weapon)
    if any(type(flag) is not bool for flag in flags):
        raise TypeError("All attack-provenance flags must be boolean")
    if magical_power or elven_combat_weapon:
        return BlubberyMassEvidence(False, Fraction(0), Fraction(1), None)
    target = 4 if elven_missile_weapon else 3
    prevention = Fraction(7 - target, 6)
    return BlubberyMassEvidence(True, prevention, 1 - prevention, target)
