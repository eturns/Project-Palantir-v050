from dataclasses import dataclass
from enum import Enum


class EngagementRole(Enum):
    CHARGED = "CHARGED"
    WAS_CHARGED = "WAS_CHARGED"


@dataclass(frozen=True)
class CombatContext:
    engagement_role: EngagementRole

    charged_only_infantry: bool = False
    resolving_exclusively_against_infantry: bool = False
    in_difficult_terrain: bool = False
    transfixed: bool = False
    fighting_across_defended_barrier: bool = False

    # Mirkwood profile-only melee rules require explicit combat state.
    # None means unknown; no outnumbering bonus may be inferred.
    outnumbered_in_combat: bool | None = None
    engaged_enemy_models: int | None = None

    def __post_init__(self) -> None:
        if (
            self.engaged_enemy_models is not None
            and (type(self.engaged_enemy_models) is not int or self.engaged_enemy_models < 1)
        ):
            raise ValueError("engaged_enemy_models must be a positive integer.")
        if self.outnumbered_in_combat is True and self.engaged_enemy_models is None:
            raise ValueError("Outnumbering bonus requires engaged_enemy_models.")
