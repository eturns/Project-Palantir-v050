"""DEV-077-TT-D4A: first three Three Trolls paid upgrade mechanics.

2024 Armies of the Hobbit p.158. Uses validated HoardEvidence, not raw
unverified upgrade strings. Pure diagnostics; no mutation of army or ratings.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction
from three_trolls_hoard import HoardEvidence

TROLL_PROFILE_IDS = frozenset({'TT_BILL', 'TT_BERT', 'TT_TOM'})
ENDURANCE_IGNORE_CHANCE = Fraction(1, 6)


def _ensure_troll(profile_id: str) -> None:
    if profile_id not in TROLL_PROFILE_IDS:
        raise ValueError('Upgrade effect requires Bill, Bert or Tom')


def _ensure_hoard(hoard: HoardEvidence) -> None:
    if not isinstance(hoard, HoardEvidence) or hoard.army_list_id != 'THREE_TROLLS':
        raise TypeError('Validated Three Trolls HoardEvidence required')


@dataclass(frozen=True)
class HeroicResourceEvidence:
    profile_id: str
    upgraded: bool
    starting_might: int
    starting_will: int
    starting_fate: int


def full_bellies_starting_resources(
    hoard: HoardEvidence, profile_id: str, *,
    base_might: int, base_will: int, base_fate: int,
) -> HeroicResourceEvidence:
    """Upgrade replaces all THREE starting resources with 3 (not +3)."""
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    for value in (base_might, base_will, base_fate):
        if type(value) is not int or value < 0:
            raise ValueError('Base resources must be non-negative integers')
    active = hoard.has('Full Bellies')
    return HeroicResourceEvidence(
        profile_id, active,
        3 if active else base_might,
        3 if active else base_will,
        3 if active else base_fate,
    )


@dataclass(frozen=True)
class EnduranceEvidence:
    profile_id: str
    upgraded: bool
    wound_occurred: bool | None
    natural_roll: int | None
    ignored: bool | None
    probability_ignored_given_wound: Fraction
    probability_not_ignored_given_wound: Fraction


def stone_troll_endurance(
    hoard: HoardEvidence, profile_id: str, *,
    wound_occurred: bool | None = None, natural_roll: int | None = None,
) -> EnduranceEvidence:
    """Each *wound* gets its own natural-6 check. No Fate inference."""
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if wound_occurred is not None and type(wound_occurred) is not bool:
        raise TypeError('wound_occurred must be bool or None')
    if natural_roll is not None:
        if type(natural_roll) is not int or not 1 <= natural_roll <= 6:
            raise ValueError('Natural D6 roll must be from 1 to 6')
        if wound_occurred is not True:
            raise ValueError('Roll requires an actual wound')
    active = hoard.has('Stone Troll Endurance')
    if not active and natural_roll is not None:
        raise ValueError('Cannot roll unpurchased Stone Troll Endurance')
    ignored = None
    if wound_occurred is False:
        ignored = False
    elif wound_occurred is True and not active:
        ignored = False
    elif wound_occurred is True and natural_roll is not None:
        ignored = natural_roll == 6
    chance = ENDURANCE_IGNORE_CHANCE if active else Fraction(0)
    return EnduranceEvidence(profile_id, active, wound_occurred,
                             natural_roll, ignored, chance, 1 - chance)


@dataclass(frozen=True)
class MomentumEvidence:
    profile_id: str
    upgraded: bool
    charged_this_turn: bool | None
    attacks: int | None
    status: str


def rumbling_momentum(
    hoard: HoardEvidence, profile_id: str, *,
    base_attacks: int, charged_this_turn: bool | None = None,
) -> MomentumEvidence:
    """Attacks BECOME 4 when purchased and charged; not +4."""
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if type(base_attacks) is not int or base_attacks < 1:
        raise ValueError('base_attacks must be positive integer')
    if charged_this_turn is not None and type(charged_this_turn) is not bool:
        raise TypeError('charged_this_turn must be bool or None')
    active = hoard.has('Rumbling Momentum')
    if active and charged_this_turn is None:
        return MomentumEvidence(profile_id, True, None, None, 'conditional_not_evaluated')
    return MomentumEvidence(profile_id, active, charged_this_turn,
                            4 if active and charged_this_turn else base_attacks,
                            'evaluated')
