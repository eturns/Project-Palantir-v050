"""DEV-077-GT-C2B: Goblin King's Goblin Projectile.

Explicit battlefield event resolver. Reuses Palantir's hit, in-the-way,
and wound tables without registering a fictional carried ranged weapon.
"""
from dataclasses import dataclass
from fractions import Fraction
from math import isfinite

from shooting_hit_probability import get_shooting_hit_probability_for_profile
from in_the_way_probability import get_in_the_way_success_probability
from wound_table import get_wound_target
from wound_probability import get_wound_probability

KING_ID = "GT_KING"
RANGE_INCHES = 12
STRENGTH = 8


@dataclass(frozen=True)
class ProjectileContext:
    friendly_model_id: str
    friendly_is_goblin: bool
    base_contact_confirmed: bool
    king_engaged: bool
    friendly_engaged: bool
    distance_inches: float
    target_defence: int
    in_the_way_required_rolls: tuple[int, ...] = ()
    to_hit_modifier: int = 0

    def __post_init__(self):
        if not isinstance(self.friendly_model_id, str) or not self.friendly_model_id.strip():
            raise ValueError("friendly_model_id is required")
        for name in ("friendly_is_goblin", "base_contact_confirmed",
                     "king_engaged", "friendly_engaged"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        if (isinstance(self.distance_inches, bool)
                or not isinstance(self.distance_inches, (int, float))
                or not isfinite(self.distance_inches) or self.distance_inches < 0):
            raise ValueError("distance_inches must be finite and nonnegative")
        if type(self.target_defence) is not int or not 1 <= self.target_defence <= 10:
            raise ValueError("target_defence must be integer from 1 to 10")
        if type(self.to_hit_modifier) is not int:
            raise TypeError("to_hit_modifier must be integer")
        if not isinstance(self.in_the_way_required_rolls, tuple):
            raise TypeError("in_the_way_required_rolls must be tuple")
        for roll in self.in_the_way_required_rolls:
            if type(roll) is not int or not 2 <= roll <= 6:
                raise ValueError("In-the-way rolls must be integers 2 through 6")


@dataclass(frozen=True)
class ProjectileEvidence:
    consumed_model_id: str
    attack_strength: int
    maximum_range_inches: int
    counts_as_throwing_weapon: bool
    probability_target_hit: Fraction
    probability_target_wounded: Fraction
    prone_if_hit: bool
    resolved_hit: bool | None = None
    # None = no actual roll resolved; this is prospective probability evidence.


def _is_king(model) -> bool:
    configured = getattr(model, "active_configured_profile", model)
    return getattr(getattr(configured, "profile", None), "id", None) == KING_ID


def can_launch_projectile(king, context: ProjectileContext) -> bool:
    if not isinstance(context, ProjectileContext):
        raise TypeError("Expected ProjectileContext")
    return (
        _is_king(king)
        and context.friendly_is_goblin
        and context.base_contact_confirmed
        and not context.king_engaged
        and not context.friendly_engaged
        and context.distance_inches <= RANGE_INCHES
    )


def assess_goblin_projectile(king, context: ProjectileContext) -> ProjectileEvidence:
    """Assess eligible, explicitly supplied firing event; no state mutation.

    Friendly model is removed when the attack is actually declared, whether
    the projectile hits or misses. Caller must apply that casualty.
    """
    if not can_launch_projectile(king, context):
        raise ValueError("Goblin Projectile cannot be fired in this context")
    configured = getattr(king, "active_configured_profile", king)
    hit = get_shooting_hit_probability_for_profile(
        configured, modifier=context.to_hit_modifier,
    )
    for required in context.in_the_way_required_rolls:
        hit *= get_in_the_way_success_probability(required_roll=required)
    wound = get_wound_probability(
        get_wound_target(strength=STRENGTH, defence=context.target_defence)
    )
    return ProjectileEvidence(
        consumed_model_id=context.friendly_model_id,
        attack_strength=STRENGTH,
        maximum_range_inches=RANGE_INCHES,
        counts_as_throwing_weapon=True,
        probability_target_hit=hit,
        probability_target_wounded=hit * wound,
        prone_if_hit=True,
    )


def resolve_projectile_hit(evidence: ProjectileEvidence, *, hit: bool) -> ProjectileEvidence:
    """Attach a confirmed hit/miss to evidence; target still requires state application."""
    if not isinstance(evidence, ProjectileEvidence):
        raise TypeError("Expected ProjectileEvidence")
    if type(hit) is not bool:
        raise TypeError("hit must be bool")
    from dataclasses import replace
    return replace(evidence, resolved_hit=hit)
