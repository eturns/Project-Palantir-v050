"""DEV-077-GT-C3A: Grinnah's Swap with Me! (2024).

Event evidence, not a geometry engine. A successful swap does not count as
movement. Caller must perform the actual position exchange.
"""
from dataclasses import dataclass
from math import isfinite

GRINNAH_ID = "GT_GRINNAH"
RULE_ID = "SWAP_WITH_ME"
MAX_RANGE_INCHES = 3
REQUIRED_BASE_MM = 25


@dataclass(frozen=True)
class GrinnahSwapContext:
    friendly_model_is_goblin: bool
    distance_inches: float
    target_base_size_mm: int
    start_of_fight_phase: bool
    before_heroic_actions: bool

    def __post_init__(self):
        for name in ("friendly_model_is_goblin", "start_of_fight_phase",
                     "before_heroic_actions"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be boolean")
        if (type(self.distance_inches) not in (int,float)
                or not isfinite(self.distance_inches)
                or self.distance_inches < 0):
            raise ValueError("distance_inches must be finite and nonnegative")
        if type(self.target_base_size_mm) is not int or self.target_base_size_mm <= 0:
            raise ValueError("target_base_size_mm must be positive integer")


@dataclass(frozen=True)
class GrinnahSwapEvidence:
    permitted: bool
    swaps_positions: bool
    counts_as_moving: bool = False


def assess_grinnah_swap(grinnah, context: GrinnahSwapContext) -> GrinnahSwapEvidence:
    if not isinstance(context, GrinnahSwapContext):
        raise TypeError("Expected GrinnahSwapContext")
    configured = getattr(grinnah, "active_configured_profile", grinnah)
    is_grinnah = getattr(getattr(configured, "profile", None), "id", None) == GRINNAH_ID
    permitted = (
        is_grinnah
        and context.start_of_fight_phase
        and context.before_heroic_actions
        and context.friendly_model_is_goblin
        and context.target_base_size_mm == REQUIRED_BASE_MM
        and context.distance_inches <= MAX_RANGE_INCHES
    )
    return GrinnahSwapEvidence(permitted=permitted, swaps_positions=permitted)
