from dataclasses import dataclass

from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from profiles import Profile


@dataclass(frozen=True)
class ScenarioContext:
    """
    Defines the static inputs required to evaluate
    scenario capability for an army candidate.
    """

    army_list: ArmyList
    key_profile: Profile
    combat_benchmark: CombatBenchmark
    benchmark_presence: int | float
    benchmark_manoeuvrability: int | float
    benchmark_combat_capability: int | float
    benchmark_fate: int | float