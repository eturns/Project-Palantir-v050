from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile

DEADLY_SHOT_RULE_ID = "DEADLY_SHOT"

@dataclass(frozen=True)
class ShootingContext:
    """
    Describes situational state relevant to whether a model
    may make a shooting attack.
    """

    moved_this_turn: bool = False
    engaged_in_combat: bool = False
    target_distance_inches: float | None = None

    def __post_init__(self) -> None:
        if (
            self.target_distance_inches is not None
            and self.target_distance_inches < 0
        ):
            raise ValueError(
                "target_distance_inches cannot be negative."
            )

def can_shoot(
    *,
    shooter: ConfiguredProfile,
    weapon: RangedWeaponProfile,
    context: ShootingContext,
) -> bool:
    if not weapon.is_mechanically_complete:
        return False

    if context.engaged_in_combat:
        has_deadly_shot = any(
            assignment.rule.id == DEADLY_SHOT_RULE_ID
            for assignment in shooter.effective_special_rules
        )

        if not has_deadly_shot:
            return False

    if (
        context.target_distance_inches is not None
        and context.target_distance_inches
        > weapon.range_inches
    ):
        return False

    if (
        weapon.requires_stationary
        and context.moved_this_turn
    ):
        return False

    return True