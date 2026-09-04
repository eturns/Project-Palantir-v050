from scenario_definition import (
    DeploymentType,
    ScenarioDefinition,
    ScenarioPool,
    ScenarioRule,
    TerminationType,
)
from scenario_demand import (
    ScenarioDemand,
    StrategicDemand,
)
from object_interaction import ObjectInteractionMode

OFFICIAL_SCENARIOS = (
    ScenarioDefinition(
        id="DOMINATION",
        name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="CAPTURE_AND_CONTROL",
        name="Capture & Control",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="BREAKTHROUGH",
        name="Breakthrough",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="STAKE_A_CLAIM",
        name="Stake a Claim",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                intensity=1.0,
            ),
        ),
    ),

    ScenarioDefinition(
        id="TO_THE_DEATH",
        name="To the Death!",
        pool=ScenarioPool.KILL_THE_ENEMY,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.ATTRITION_OUTPUT,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.STATE_RESILIENCE,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="LORDS_OF_BATTLE",
        name="Lords of Battle",
        pool=ScenarioPool.KILL_THE_ENEMY,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
        special_rules=(
            ScenarioRule.A_TIME_OF_HEROES,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.ATTRITION_OUTPUT,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.STATE_RESILIENCE,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="ASSASSINATION",
        name="Assassination",
        pool=ScenarioPool.KILL_THE_ENEMY,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
        special_rules=(
            ScenarioRule.DARK_OF_NIGHT,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.KEY_MODEL_PRESSURE,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="CONTEST_OF_CHAMPIONS",
        name="Contest of Champions",
        pool=ScenarioPool.KILL_THE_ENEMY,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.A_TIME_OF_HEROES,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.KEY_MODEL_PRESSURE,
                intensity=1.0,
            ),
        ),
    ),

   ScenarioDefinition(
        id="HOLD_GROUND",
        name="Hold Ground",
        pool=ScenarioPool.MAELSTROM_OF_BATTLE,
        deployment_type=DeploymentType.MAELSTROM,
        termination_type=TerminationType.BROKEN_RANDOM,
        special_rules=(
            ScenarioRule.MAELSTROM_OF_BATTLE,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="HEIRLOOM_OF_AGES_PAST",
        name="Heirloom of Ages Past",
        pool=ScenarioPool.MAELSTROM_OF_BATTLE,
        deployment_type=DeploymentType.MAELSTROM,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.MAELSTROM_OF_BATTLE,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.SEARCH_AND_LIGHT_OBJECT,
    ),
    ScenarioDefinition(
        id="SITES_OF_POWER",
        name="Sites of Power",
        pool=ScenarioPool.MAELSTROM_OF_BATTLE,
        deployment_type=DeploymentType.MAELSTROM,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.DARK_OF_NIGHT,
            ScenarioRule.MAELSTROM_OF_BATTLE,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="COMMAND_THE_BATTLEFIELD",
        name="Command the Battlefield",
        pool=ScenarioPool.MAELSTROM_OF_BATTLE,
        deployment_type=DeploymentType.MAELSTROM,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.MAELSTROM_OF_BATTLE,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                intensity=1.0,
            ),
        ),
    ),

    ScenarioDefinition(
        id="DESTROY_THE_SUPPLIES",
        name="Destroy the Supplies",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.CONCENTRATED_CONTROL,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.STATIC_ACTION,
    ),
    ScenarioDefinition(
        id="RETRIEVAL",
        name="Retrieval",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.STATE_RESILIENCE,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.LIGHT_OBJECT,
    ),
    ScenarioDefinition(
        id="SEIZE_THE_PRIZES",
        name="Seize the Prizes",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.SCENARIO_SPECIFIC,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.UNCOVER_AND_LIGHT_OBJECT,
    ),
    ScenarioDefinition(
        id="TREASURE_HOARD",
        name="Treasure Hoard",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.UNCOVER_AND_LIGHT_OBJECT,
    ),

    ScenarioDefinition(
        id="RECONNOITRE",
        name="Reconnoitre",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.REINFORCEMENTS,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="STORM_THE_CAMP",
        name="Storm the Camp",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.CONCENTRATED_CONTROL,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="DIVIDE_AND_CONQUER",
        name="Divide & Conquer",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.SPLIT,
        termination_type=TerminationType.BROKEN_RANDOM,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="ESCORT_THE_WOUNDED",
        name="Escort the Wounded",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.HEAVY_OBJECT, 
    ),

    ScenarioDefinition(
        id="FOG_OF_WAR",
        name="Fog of War",
        pool=ScenarioPool.UNIQUE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.CONCENTRATED_CONTROL,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.KEY_MODEL_PRESSURE,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="CLASH_BY_MOONLIGHT",
        name="Clash by Moonlight",
        pool=ScenarioPool.UNIQUE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.DARK_OF_NIGHT,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.PROJECTION,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="LEAD_FROM_THE_FRONT",
        name="Lead from the Front",
        pool=ScenarioPool.UNIQUE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.A_TIME_OF_HEROES,
        ),
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
                intensity=1.0,
            ),
        ),
    ),
    ScenarioDefinition(
        id="CONVERGENCE",
        name="Convergence",
        pool=ScenarioPool.UNIQUE,
        deployment_type=DeploymentType.SPLIT,
        termination_type=TerminationType.BROKEN_RANDOM,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.OBJECT_INTERACTION,
                intensity=1.0,
            ),
        ),
        object_interaction_mode=ObjectInteractionMode.LIGHT_OBJECT,
        
    ),
)


def get_official_scenarios() -> tuple[ScenarioDefinition, ...]:
    return OFFICIAL_SCENARIOS

def get_official_scenario(
    scenario_id: str,
) -> ScenarioDefinition:
    if not scenario_id.strip():
        raise ValueError(
            "Scenario ID cannot be blank."
        )

    for scenario in OFFICIAL_SCENARIOS:
        if scenario.id == scenario_id:
            return scenario

    raise ValueError(
        f"Unknown official scenario ID: {scenario_id}"
    )

def get_official_scenarios_by_pool(
    pool: ScenarioPool,
) -> tuple[ScenarioDefinition, ...]:
    if not isinstance(
        pool,
        ScenarioPool,
    ):
        raise TypeError(
            "pool must be a ScenarioPool."
        )

    return tuple(
        scenario
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is pool
    )