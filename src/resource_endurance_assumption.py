from dataclasses import dataclass

from battle_length_assumption import BattleHorizon
from resource_strategy import ResourceStrategy


@dataclass(frozen=True)
class ResourceEnduranceAssumption:
    horizon: BattleHorizon
    strategy: ResourceStrategy