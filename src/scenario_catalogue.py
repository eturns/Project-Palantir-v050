from scenario_definition import (
    DeploymentType,
    ScenarioDefinition,
    ScenarioPool,
    ScenarioRule,
    TerminationType,
)


OFFICIAL_SCENARIOS = (
    ScenarioDefinition(
        id="DOMINATION",
        name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),
    ScenarioDefinition(
        id="CAPTURE_AND_CONTROL",
        name="Capture & Control",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
    ),
    ScenarioDefinition(
        id="BREAKTHROUGH",
        name="Breakthrough",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),
    ScenarioDefinition(
        id="STAKE_A_CLAIM",
        name="Stake a Claim",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),

    ScenarioDefinition(
        id="TO_THE_DEATH",
        name="To the Death!",
        pool=ScenarioPool.KILL_THE_ENEMY,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
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
    ),

    ScenarioDefinition(
        id="DESTROY_THE_SUPPLIES",
        name="Destroy the Supplies",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),
    ScenarioDefinition(
        id="RETRIEVAL",
        name="Retrieval",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
    ),
    ScenarioDefinition(
        id="SEIZE_THE_PRIZES",
        name="Seize the Prizes",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.SCENARIO_SPECIFIC,
    ),
    ScenarioDefinition(
        id="TREASURE_HOARD",
        name="Treasure Hoard",
        pool=ScenarioPool.OBJECT,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),

    ScenarioDefinition(
        id="RECONNOITRE",
        name="Reconnoitre",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.REINFORCEMENTS,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),
    ScenarioDefinition(
        id="STORM_THE_CAMP",
        name="Storm the Camp",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),
    ScenarioDefinition(
        id="DIVIDE_AND_CONQUER",
        name="Divide & Conquer",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.SPLIT,
        termination_type=TerminationType.BROKEN_RANDOM,
    ),
    ScenarioDefinition(
        id="ESCORT_THE_WOUNDED",
        name="Escort the Wounded",
        pool=ScenarioPool.MANOEUVRING,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    ),

    ScenarioDefinition(
        id="FOG_OF_WAR",
        name="Fog of War",
        pool=ScenarioPool.UNIQUE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.BROKEN_RANDOM,
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
    ),
    ScenarioDefinition(
        id="CONVERGENCE",
        name="Convergence",
        pool=ScenarioPool.UNIQUE,
        deployment_type=DeploymentType.SPLIT,
        termination_type=TerminationType.BROKEN_RANDOM,
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