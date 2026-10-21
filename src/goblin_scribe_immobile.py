"""DEV-077-GT-C3B1: Goblin Scribe's Immobile rule.

Battlefield-event evidence only: carrying geometry, legal carriers and
object placement must be validated by the calling battlefield system.
"""
from dataclasses import dataclass

SCRIBE_ID = "GT_SCRIBE"
RULE_ID = "IMMOBILE"


@dataclass(frozen=True)
class ScribeImmobileEvidence:
    immobile_rule_active: bool
    may_move_independently: bool
    counts_as_trapped_if_duel_lost: bool
    may_be_carried_as_heavy_object: bool
    must_be_put_down_after_carrier_move: bool
    may_be_carried_onto_board: bool


@dataclass(frozen=True)
class ScribeCarryingContext:
    carrier_is_friendly: bool
    carrying_allowed_by_heavy_object_rules: bool
    carrier_finished_move: bool
    entering_board_via_scenario: bool = False

    def __post_init__(self):
        for name in (
            "carrier_is_friendly",
            "carrying_allowed_by_heavy_object_rules",
            "carrier_finished_move",
            "entering_board_via_scenario",
        ):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be boolean")


@dataclass(frozen=True)
class ScribeCarryingEvidence:
    can_carry: bool
    must_put_down_now: bool
    entering_board_by_carrier_permitted: bool


def assess_scribe_immobile(combatant) -> ScribeImmobileEvidence | None:
    """Return a rule contract for a Scribe with the rule assigned.

    Missing rules are not silently treated as applying.
    """
    configured = getattr(combatant, "active_configured_profile", combatant)
    profile = getattr(configured, "profile", None)
    if getattr(profile, "id", None) != SCRIBE_ID:
        return None
    rule_ids = {
        getattr(getattr(assignment, "rule", None), "id", None)
        for assignment in getattr(configured, "effective_special_rules", ())
    }
    if RULE_ID not in rule_ids:
        raise ValueError("Goblin Scribe must have IMMOBILE assigned in canonical rule data")
    return ScribeImmobileEvidence(
        immobile_rule_active=True,
        may_move_independently=False,
        counts_as_trapped_if_duel_lost=True,
        may_be_carried_as_heavy_object=True,
        must_be_put_down_after_carrier_move=True,
        may_be_carried_onto_board=True,
    )


def assess_scribe_carrying(combatant, context: ScribeCarryingContext) -> ScribeCarryingEvidence:
    """Assess an explicitly supplied carrying event; never moves the model."""
    if not isinstance(context, ScribeCarryingContext):
        raise TypeError("Expected ScribeCarryingContext")
    scribe = assess_scribe_immobile(combatant)
    if scribe is None:
        return ScribeCarryingEvidence(False, False, False)
    can_carry = (
        context.carrier_is_friendly
        and context.carrying_allowed_by_heavy_object_rules
    )
    return ScribeCarryingEvidence(
        can_carry=can_carry,
        must_put_down_now=can_carry and context.carrier_finished_move,
        entering_board_by_carrier_permitted=can_carry and context.entering_board_via_scenario,
    )
