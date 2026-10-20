"""Gundabad Ogre Relentless Advance: explicit charge-path outcomes."""
from dataclasses import dataclass
from fractions import Fraction
from wound_table import get_wound_target
from wound_probability import get_wound_probability

RULE_ID = 'RELENTLESS_ADVANCE'
OGRE_ID = 'GUNDABAD_OGRE'
ELIGIBLE_RACES = frozenset({'ORC', 'GOBLIN', 'BAT'})

@dataclass(frozen=True)
class FriendlyContact:
    model_id: str
    races: frozenset[str]
    defence: int
    overlapped_at_end: bool = False

    def __post_init__(self):
        if not self.model_id:
            raise ValueError('model_id must be nonempty')
        if type(self.defence) is not int or not 1 <= self.defence <= 10:
            raise ValueError('defence must be an integer from 1 to 10')
        if type(self.overlapped_at_end) is not bool:
            raise TypeError('overlapped_at_end must be a bool')

@dataclass(frozen=True)
class RelentlessAdvanceOutcome:
    model_id: str
    strength: int
    wound_probability: Fraction
    automatically_slain: bool


def resolve_relentless_advance(
    ogre, contacts: tuple[FriendlyContact, ...], *,
    charging_into_combat: bool, forced_by_enemy_effect: bool = False,
) -> tuple[RelentlessAdvanceOutcome, ...]:
    """One S3 hit per passed-through friend; final overlaps automatically slain.

    This is a planning/event resolver, not a geometry engine or state mutator.
    Caller must supply verified friendly path intersections and final overlaps.
    """
    if type(charging_into_combat) is not bool or type(forced_by_enemy_effect) is not bool:
        raise TypeError('Movement flags must be bool')
    if getattr(getattr(ogre, 'profile', None), 'id', None) != OGRE_ID:
        return ()
    if RULE_ID not in {
        getattr(getattr(a, 'rule', None), 'id', None)
        for a in getattr(ogre, 'effective_special_rules', ())
    }:
        return ()
    if not charging_into_combat or forced_by_enemy_effect:
        return ()
    seen = set()
    outcomes = []
    for contact in contacts:
        if not isinstance(contact, FriendlyContact):
            raise TypeError('Each contact must be a FriendlyContact')
        if contact.model_id in seen:
            raise ValueError('Duplicate friendly model in charge path')
        seen.add(contact.model_id)
        if not {str(r).upper() for r in contact.races} & ELIGIBLE_RACES:
            raise ValueError('Cannot move through that friendly race')
        outcomes.append(RelentlessAdvanceOutcome(
            model_id=contact.model_id,
            strength=3,
            wound_probability=get_wound_probability(get_wound_target(3, contact.defence)),
            automatically_slain=contact.overlapped_at_end,
        ))
    return tuple(outcomes)
