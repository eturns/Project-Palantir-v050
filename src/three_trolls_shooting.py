"""DEV-077-TT-D1B: conditional Three Trolls shooting rules.

Throw Stones is an innate shooting attack, not purchased wargear.
Large Target filters model obstructions; terrain and shooting-into-combat
checks still apply. This module never confers a blanket hit bonus.
"""
from __future__ import annotations

from dataclasses import dataclass
from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile

THROW_STONES_RULE_ID = "THROW_STONES"
LARGE_TARGET_RULE_ID = "LARGE_TARGET"
THROW_STONES_WEAPON_ID = "RULE_THROW_STONES"
THROW_STONES_WEAPON = RangedWeaponProfile(
    wargear_id=THROW_STONES_WEAPON_ID,
    range_inches=12,
    strength=8,
    shots=1,
    requires_stationary=True,
)
LARGE_OBSTRUCTION_KEYWORDS = frozenset({"MONSTER", "SIEGE_ENGINE", "WAR_BEAST"})


def has_rule(profile: ConfiguredProfile, rule_id: str) -> bool:
    return any(assignment.rule.id == rule_id for assignment in profile.effective_special_rules)


def get_throw_stones_weapon(profile: ConfiguredProfile) -> RangedWeaponProfile | None:
    """Return innate stone attack only for a rule-bearing model."""
    return THROW_STONES_WEAPON if has_rule(profile, THROW_STONES_RULE_ID) else None


@dataclass(frozen=True)
class ModelObstruction:
    """One model between the shooter and target and its in-the-way threshold."""
    required_roll: int
    keywords: frozenset[str]

    def __post_init__(self) -> None:
        if not 2 <= self.required_roll <= 6:
            raise ValueError("In-the-way target must be 2 through 6.")
        if any(not isinstance(k, str) for k in self.keywords):
            raise ValueError("Obstruction keywords must be strings.")


def large_target_in_the_way_rolls(
    *,
    defender: ConfiguredProfile,
    model_obstructions: tuple[ModelObstruction, ...] = (),
    terrain_required_rolls: tuple[int, ...] = (),
    shooting_into_combat_required_roll: int | None = None,
) -> tuple[int, ...]:
    """Filter only smaller intervening *models* when defender is a Large Target.

    Explicit terrain and combat obstruction rolls remain untouched. The caller
    is responsible for determining actual geometry and applicable obstructions.
    """
    for value in terrain_required_rolls:
        if not 2 <= value <= 6:
            raise ValueError("Terrain in-the-way roll must be 2 through 6.")
    if shooting_into_combat_required_roll is not None and not 2 <= shooting_into_combat_required_roll <= 6:
        raise ValueError("Combat in-the-way roll must be 2 through 6.")
    is_large = has_rule(defender, LARGE_TARGET_RULE_ID)
    model_rolls = tuple(
        item.required_roll for item in model_obstructions
        if not is_large or bool({x.upper().replace(" ", "_") for x in item.keywords} & LARGE_OBSTRUCTION_KEYWORDS)
    )
    return (
        terrain_required_rolls + model_rolls +
        (() if shooting_into_combat_required_roll is None else (shooting_into_combat_required_roll,))
    )
