"""Gundabad Catapult Troll Metal Gauntlets, 2024 rules.

Normal strikes are Strength 10. Hurl distance is D3 plus Strength
advantage; Metal Gauntlets allow that D3 to be rerolled once.
"""
from dataclasses import dataclass
from fractions import Fraction
from wound_table import get_wound_target
from wound_probability import get_wound_probability

CATAPULT_TROLL_NAME = 'Gundabad Catapult Troll'
GAUNTLETS_NAME = 'Metal Gauntlets'


def has_metal_gauntlets(combatant) -> bool:
    cfg = getattr(combatant, 'active_configured_profile', combatant)
    profile = getattr(cfg, 'profile', None)
    return (getattr(profile, 'name', '').casefold() == CATAPULT_TROLL_NAME.casefold()
            and any(getattr(g, 'name', '').casefold() == GAUNTLETS_NAME.casefold()
                    for g in getattr(cfg, 'effective_wargear', ())))


def melee_strike_strength(combatant, *, normal_strike: bool = True) -> int:
    """This must not be used for shooting, Impact Hits or Hurl's S6 hits."""
    cfg = getattr(combatant, 'active_configured_profile', combatant)
    return 10 if normal_strike and has_metal_gauntlets(combatant) else cfg.effective_strength


def metal_gauntlets_wound_probability(combatant, defence: int) -> Fraction:
    return get_wound_probability(get_wound_target(melee_strike_strength(combatant), defence))


def hurl_distance(strength: int, target_strength: int, d3: int) -> int:
    if any(type(v) is not int for v in (strength, target_strength, d3)):
        raise TypeError('Hurl values must be integers.')
    if not 1 <= strength <= 10 or not 1 <= target_strength <= 10:
        raise ValueError('Strengths must be 1..10.')
    if strength <= target_strength:
        raise ValueError('Cannot Hurl an equal-or-higher-Strength model.')
    if d3 not in (1, 2, 3):
        raise ValueError('D3 roll must be 1, 2 or 3.')
    return strength - target_strength + d3


@dataclass(frozen=True)
class HurlDistanceRoll:
    first_d3: int
    reroll_d3: int | None = None

    def __post_init__(self):
        for value in (self.first_d3, self.reroll_d3):
            if value is not None and (type(value) is not int or value not in (1, 2, 3)):
                raise ValueError('Each D3 result must be 1, 2 or 3.')


def gauntlets_hurl_distance(combatant, target_strength: int, roll: HurlDistanceRoll) -> int:
    """Optional reroll is binding: never automatically keep the higher die."""
    if not has_metal_gauntlets(combatant):
        raise ValueError('Metal Gauntlets are required.')
    if not isinstance(roll, HurlDistanceRoll):
        raise TypeError('Expected HurlDistanceRoll.')
    cfg = getattr(combatant, 'active_configured_profile', combatant)
    d3 = roll.reroll_d3 if roll.reroll_d3 is not None else roll.first_d3
    return hurl_distance(cfg.effective_strength, target_strength, d3)
