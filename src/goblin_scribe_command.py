"""DEV-077-GT-C3B2: Goblin Scribe's The Goblin King's Command.

Conditional event resolvers; no positional inference, state mutation, or scores.
"""
from dataclasses import dataclass
from math import isfinite

KING_ID = "GT_KING"
SCRIBE_ID = "GT_SCRIBE"
COMMAND_RULE_ID = "THE_GOBLIN_KINGS_COMMAND"

def _valid_distance(value, name):
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and nonnegative")

def _id(combatant):
    cfg = getattr(combatant, "active_configured_profile", combatant)
    return getattr(getattr(cfg, "profile", None), "id", None)

@dataclass(frozen=True)
class WithMeContext:
    distance_king_to_scribe_inches: float
    king_declared_heroic_move: bool
    king_called_with_me: bool

    def __post_init__(self):
        _valid_distance(self.distance_king_to_scribe_inches, "distance")
        for name in ("king_declared_heroic_move", "king_called_with_me"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")

@dataclass(frozen=True)
class WithMeEvidence:
    battlefield_wide_friendly_models: bool
    removes_king_end_distance_requirement: bool

def assess_with_me_extension(king, scribe, context: WithMeContext) -> WithMeEvidence:
    if not isinstance(context, WithMeContext):
        raise TypeError("Expected WithMeContext")
    valid=(
        _id(king) == KING_ID and _id(scribe) == SCRIBE_ID
        and context.distance_king_to_scribe_inches <= 6
        and context.king_declared_heroic_move
        and context.king_called_with_me
    )
    return WithMeEvidence(valid, valid)

@dataclass(frozen=True)
class MightTransferContext:
    hero_is_friendly_goblin: bool
    hero_is_hero: bool
    hero_started_activation_within_scribe_inches: float
    hero_might_remaining: int
    king_might_spent: int
    used_this_turn: bool
    hero_chooses_to_spend_might: bool

    def __post_init__(self):
        _valid_distance(self.hero_started_activation_within_scribe_inches, "distance")
        for name in ("hero_is_friendly_goblin", "hero_is_hero",
                     "used_this_turn", "hero_chooses_to_spend_might"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        for name in ("hero_might_remaining", "king_might_spent"):
            val=getattr(self,name)
            if type(val) is not int or val < 0:
                raise ValueError(f"{name} must be nonnegative integer")

@dataclass(frozen=True)
class MightTransferEvidence:
    eligible: bool
    hero_might_spent: int
    king_might_recovered: int
    consumes_once_per_turn_use: bool

def assess_might_transfer(king, scribe, context: MightTransferContext) -> MightTransferEvidence:
    if not isinstance(context, MightTransferContext):
        raise TypeError("Expected MightTransferContext")
    eligible=(
        _id(king)==KING_ID and _id(scribe)==SCRIBE_ID
        and context.hero_is_friendly_goblin and context.hero_is_hero
        and context.hero_started_activation_within_scribe_inches <= 3
        and context.hero_might_remaining >= 1 and context.king_might_spent >= 1
        and not context.used_this_turn and context.hero_chooses_to_spend_might
    )
    return MightTransferEvidence(eligible, int(eligible), int(eligible), eligible)
