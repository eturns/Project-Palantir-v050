"""DEV-077-GT-C2C: Goblin King's Relentless Advance.

Uses existing contact and wound evidence structures. All path contacts must be
explicitly supplied and confirmed friendly by the caller; no geometry is inferred.
"""
from gundabad_relentless_advance import FriendlyContact, RelentlessAdvanceOutcome
from wound_probability import get_wound_probability
from wound_table import get_wound_target

KING_PROFILE_ID = "GT_KING"
RULE_ID = "RELENTLESS_ADVANCE"


def resolve_goblin_king_relentless_advance(
    king,
    contacts: tuple[FriendlyContact, ...],
    *,
    charging_into_combat: bool,
    forced_by_enemy_effect: bool = False,
) -> tuple[RelentlessAdvanceOutcome, ...]:
    """Resolve confirmed friendly Goblin contacts on a charging path.

    Each contacted friendly Goblin suffers one S3 hit. A friendly Goblin
    overlapped at the end is automatically slain, regardless of the hit.
    This is mechanical evidence, not automatic casualty/state mutation.
    """
    if type(charging_into_combat) is not bool or type(forced_by_enemy_effect) is not bool:
        raise TypeError("Movement flags must be bool")
    if not isinstance(contacts, tuple):
        raise TypeError("contacts must be a tuple")
    if getattr(getattr(king, "profile", None), "id", None) != KING_PROFILE_ID:
        return ()
    rule_ids = {
        getattr(getattr(assignment, "rule", None), "id", None)
        for assignment in getattr(king, "effective_special_rules", ())
    }
    if RULE_ID not in rule_ids or not charging_into_combat or forced_by_enemy_effect:
        return ()

    seen = set()
    outcomes = []
    for contact in contacts:
        if not isinstance(contact, FriendlyContact):
            raise TypeError("Each contact must be FriendlyContact")
        if contact.model_id in seen:
            raise ValueError("Duplicate friendly model in charge path")
        seen.add(contact.model_id)
        if "GOBLIN" not in {str(r).upper() for r in contact.races}:
            raise ValueError("Goblin King may only pass through friendly Goblins")
        outcomes.append(RelentlessAdvanceOutcome(
            model_id=contact.model_id,
            strength=3,
            wound_probability=get_wound_probability(
                get_wound_target(3, contact.defence)
            ),
            automatically_slain=contact.overlapped_at_end,
        ))
    return tuple(outcomes)
