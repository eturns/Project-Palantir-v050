"""DEV-077-TT-D2D — Tom's Squash 'em into Jelly Brutal Power Attack.

Authority: MESBG Armies of the Hobbit (2024), Tom the Troll, PDF p. 142.
This resolver emits conditional combat effects. It does not assume a target's
remaining Wounds, Fate, saves, position, or that Tom won an unmodelled Duel.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from wound_table import get_wound_target
from wound_probability import get_wound_probability

TOM_PROFILE_ID = "TT_TOM"
SQUASH_EM_INTO_JELLY_RULE_ID = "SQUASH_EM_INTO_JELLY"
SQUASH_STRENGTH = 6


@dataclass(frozen=True)
class SquashTarget:
    """An enemy model actually engaged with Tom, supplied by the caller."""

    model_id: str
    defence: int

    def __post_init__(self) -> None:
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("Target model_id must be a nonempty string")
        if type(self.defence) is not int or not 1 <= self.defence <= 10:
            raise ValueError("Target defence must be an integer from 1 to 10")


@dataclass(frozen=True)
class SquashContext:
    attacker_profile_id: str
    attacker_won_duel: bool
    engaged_enemies: tuple[SquashTarget, ...]
    alternative_attack_already_used: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.attacker_profile_id, str) or not self.attacker_profile_id:
            raise ValueError("Attacker profile ID is required")
        if type(self.attacker_won_duel) is not bool:
            raise ValueError("attacker_won_duel must be boolean")
        if type(self.alternative_attack_already_used) is not bool:
            raise ValueError("alternative_attack_already_used must be boolean")
        if not isinstance(self.engaged_enemies, tuple) or any(
            not isinstance(item, SquashTarget) for item in self.engaged_enemies
        ):
            raise ValueError("engaged_enemies must be a tuple of SquashTarget")
        identifiers = [item.model_id for item in self.engaged_enemies]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Each engaged enemy must be listed once")


@dataclass(frozen=True)
class SquashHit:
    target_id: str
    strength: int
    wound_probability: Fraction
    # Apply only if the target survives the hit after damage/Fate resolution.
    knock_prone_if_survives: bool = True


@dataclass(frozen=True)
class SquashResult:
    replaces_normal_strikes: bool
    hits: tuple[SquashHit, ...]
    # A separate caller must resolve actual damage, saves and prone states.
    actual_damage_evaluated: bool = False

    @property
    def expected_wounds_before_saves(self) -> Fraction:
        return sum((hit.wound_probability for hit in self.hits), Fraction(0, 1))


def resolve_squash_em_into_jelly(context: SquashContext) -> SquashResult | None:
    """Resolve one S6 hit per enemy engaged with Tom, conditional on a won Duel.

    Do not claim that Knocked Prone is applied until survival is known.
    Normal Strikes are replaced. Never award both normal Strikes and these hits.
    """
    if context.attacker_profile_id != TOM_PROFILE_ID:
        return None
    if not context.attacker_won_duel or context.alternative_attack_already_used:
        return None
    if not context.engaged_enemies:
        return None
    hits = tuple(
        SquashHit(
            target_id=target.model_id,
            strength=SQUASH_STRENGTH,
            wound_probability=get_wound_probability(
                get_wound_target(strength=SQUASH_STRENGTH, defence=target.defence)
            ),
        )
        for target in context.engaged_enemies
    )
    return SquashResult(replaces_normal_strikes=True, hits=hits)
