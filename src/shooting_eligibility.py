from dataclasses import dataclass
from configured_profile import ConfiguredProfile
from ranged_weapon_profile import RangedWeaponProfile
from shooting_attack_count import ShootingMode

DEADLY_SHOT_RULE_ID = "DEADLY_SHOT"
PINPOINT_SHOT_RULE_ID = "PINPOINT_SHOT"


@dataclass(frozen=True)
class ShootingContext:
    moved_this_turn: bool = False
    engaged_in_combat: bool = False
    target_distance_inches: float | None = None
    # Explicit target status is mandatory for Pinpoint mode.
    target_engaged_with_friendly: bool = False
    shooting_mode: ShootingMode = ShootingMode.NORMAL

    def __post_init__(self) -> None:
        if self.target_distance_inches is not None and self.target_distance_inches < 0:
            raise ValueError("target_distance_inches cannot be negative.")
        if not isinstance(self.shooting_mode, ShootingMode):
            raise ValueError("Unknown shooting mode.")


def can_shoot(
    *,
    shooter: ConfiguredProfile,
    weapon: RangedWeaponProfile,
    context: ShootingContext,
) -> bool:
    if not weapon.is_mechanically_complete:
        return False
    rules = {a.rule.id for a in shooter.effective_special_rules}
    if context.shooting_mode is ShootingMode.PINPOINT:
        if PINPOINT_SHOT_RULE_ID not in rules or not context.target_engaged_with_friendly:
            return False
    if context.engaged_in_combat and DEADLY_SHOT_RULE_ID not in rules:
        return False
    if (
        context.target_distance_inches is not None
        and context.target_distance_inches > weapon.range_inches
    ):
        return False
    if weapon.requires_stationary and context.moved_this_turn:
        return False
    return True
