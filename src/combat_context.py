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