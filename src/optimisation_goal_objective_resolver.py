from army_list import ArmyList
from balanced_objective import BalancedObjective
from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)
from board_presence_objective import (
    BoardPresenceObjective,
)
from combat_benchmark import CombatBenchmark
from magic_objective import MagicObjective
from optimisation_request import (
    OptimisationGoal,
)
from optimiser_objective import (
    OptimiserObjective,
)
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from scenario_objective import ScenarioObjective
from scenario_context import ScenarioContext

def resolve_optimisation_goal_objective(
    *,
    goal: OptimisationGoal,
    army_list: ArmyList,
    combat_benchmark: CombatBenchmark | None = None,
    resource_assumption: ResourceEnduranceAssumption | None = None,
    key_profile=None,
    benchmark_presence: int | float | None = None,
    benchmark_manoeuvrability: int | float | None = None,
    benchmark_combat_capability: int | float | None = None,
    benchmark_fate: int | float | None = None,
) -> OptimiserObjective:
    if goal is OptimisationGoal.BOARD_PRESENCE:
        return BoardPresenceObjective(
            army_list=army_list,
        )

    if goal is OptimisationGoal.MAGIC:
        return MagicObjective(
            army_list=army_list,
        )

    if goal is OptimisationGoal.BALANCED:
        if combat_benchmark is None:
            raise ValueError(
                "Balanced optimisation requires a combat benchmark."
            )

        if resource_assumption is None:
            raise ValueError(
                "Balanced optimisation requires a resource endurance assumption."
            )

        return BalancedObjective(
            preset=BALANCED_OBJECTIVE_PRESET,
            army_list=army_list,
            combat_benchmark=combat_benchmark,
            resource_assumption=resource_assumption,
        )

    if goal is OptimisationGoal.SCENARIO:
        if combat_benchmark is None:
            raise ValueError(
                "Scenario optimisation requires a combat benchmark."
            )

        if key_profile is None:
            raise ValueError(
                "Scenario optimisation requires a key profile."
            )

        if benchmark_presence is None:
            raise ValueError(
                "Scenario optimisation requires benchmark presence."
            )

        if benchmark_manoeuvrability is None:
            raise ValueError(
                "Scenario optimisation requires benchmark manoeuvrability."
            )

        if benchmark_combat_capability is None:
            raise ValueError(
                "Scenario optimisation requires benchmark combat capability."
            )

        if benchmark_fate is None:
            raise ValueError(
                "Scenario optimisation requires benchmark fate."
            )

        return ScenarioObjective(
            context=ScenarioContext(
                army_list=army_list,
                key_profile=key_profile,
                combat_benchmark=combat_benchmark,
                benchmark_presence=benchmark_presence,
                benchmark_manoeuvrability=(
                    benchmark_manoeuvrability
                ),
                benchmark_combat_capability=(
                    benchmark_combat_capability
                ),
                benchmark_fate=benchmark_fate,
            ),
        )

    raise ValueError(
        f"Unsupported optimisation goal: {goal}"
    )