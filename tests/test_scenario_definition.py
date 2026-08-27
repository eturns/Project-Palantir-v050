import pytest

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

def test_scenario_pool_contains_all_six_official_pools():
    assert ScenarioPool.HOLD_OBJECTIVE.value == "hold_objective"
    assert ScenarioPool.KILL_THE_ENEMY.value == "kill_the_enemy"
    assert ScenarioPool.MAELSTROM_OF_BATTLE.value == "maelstrom_of_battle"
    assert ScenarioPool.OBJECT.value == "object"
    assert ScenarioPool.MANOEUVRING.value == "manoeuvring"
    assert ScenarioPool.UNIQUE.value == "unique"


def test_deployment_type_contains_initial_supported_types():
    assert DeploymentType.STANDARD.value == "standard"
    assert DeploymentType.MAELSTROM.value == "maelstrom"
    assert DeploymentType.SPLIT.value == "split"
    assert DeploymentType.REINFORCEMENTS.value == "reinforcements"


def test_termination_type_contains_initial_supported_types():
    assert TerminationType.QUARTER_STRENGTH.value == "quarter_strength"
    assert (
        TerminationType.BROKEN_RANDOM.value
        == "broken_random"
    )
    assert (
        TerminationType.SCENARIO_SPECIFIC.value
        == "scenario_specific"
    )


def test_scenario_definition_stores_canonical_identity():
    scenario = ScenarioDefinition(
        id="DOMINATION",
        name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    )

    assert scenario.id == "DOMINATION"
    assert scenario.name == "Domination"
    assert scenario.pool is ScenarioPool.HOLD_OBJECTIVE
    assert scenario.deployment_type is DeploymentType.STANDARD
    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_scenario_definition_is_immutable():
    scenario = ScenarioDefinition(
        id="DOMINATION",
        name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    )

    with pytest.raises(AttributeError):
        scenario.name = "Changed"


def test_scenario_definition_rejects_blank_id():
    with pytest.raises(
        ValueError,
        match="Scenario ID cannot be blank.",
    ):
        ScenarioDefinition(
            id="",
            name="Domination",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
        )


def test_scenario_definition_rejects_blank_name():
    with pytest.raises(
        ValueError,
        match="Scenario name cannot be blank.",
    ):
        ScenarioDefinition(
            id="DOMINATION",
            name="",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
        )

def test_scenario_rule_contains_initial_common_rules():
    assert (
        ScenarioRule.MAELSTROM_OF_BATTLE.value
        == "maelstrom_of_battle"
    )
    assert (
        ScenarioRule.DARK_OF_NIGHT.value
        == "dark_of_night"
    )
    assert (
        ScenarioRule.A_TIME_OF_HEROES.value
        == "a_time_of_heroes"
    )


def test_scenario_definition_defaults_to_no_common_rules():
    scenario = ScenarioDefinition(
        id="DOMINATION",
        name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    )

    assert scenario.special_rules == ()


def test_scenario_definition_stores_common_rules():
    scenario = ScenarioDefinition(
        id="HOLD_GROUND",
        name="Hold Ground",
        pool=ScenarioPool.MAELSTROM_OF_BATTLE,
        deployment_type=DeploymentType.MAELSTROM,
        termination_type=TerminationType.BROKEN_RANDOM,
        special_rules=(
            ScenarioRule.MAELSTROM_OF_BATTLE,
        ),
    )

    assert scenario.special_rules == (
        ScenarioRule.MAELSTROM_OF_BATTLE,
    )


def test_scenario_definition_preserves_multiple_common_rules():
    scenario = ScenarioDefinition(
        id="SITES_OF_POWER",
        name="Sites of Power",
        pool=ScenarioPool.MAELSTROM_OF_BATTLE,
        deployment_type=DeploymentType.MAELSTROM,
        termination_type=TerminationType.QUARTER_STRENGTH,
        special_rules=(
            ScenarioRule.DARK_OF_NIGHT,
            ScenarioRule.MAELSTROM_OF_BATTLE,
        ),
    )

    assert scenario.special_rules == (
        ScenarioRule.DARK_OF_NIGHT,
        ScenarioRule.MAELSTROM_OF_BATTLE,
    )

def test_scenario_definition_rejects_invalid_pool_type():
    with pytest.raises(
        TypeError,
        match="pool must be a ScenarioPool.",
    ):
        ScenarioDefinition(
            id="DOMINATION",
            name="Domination",
            pool="hold_objective",
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
        )


def test_scenario_definition_rejects_invalid_deployment_type():
    with pytest.raises(
        TypeError,
        match="deployment_type must be a DeploymentType.",
    ):
        ScenarioDefinition(
            id="DOMINATION",
            name="Domination",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type="standard",
            termination_type=TerminationType.QUARTER_STRENGTH,
        )


def test_scenario_definition_rejects_invalid_termination_type():
    with pytest.raises(
        TypeError,
        match="termination_type must be a TerminationType.",
    ):
        ScenarioDefinition(
            id="DOMINATION",
            name="Domination",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type="quarter_strength",
        )


def test_scenario_definition_rejects_invalid_special_rule_type():
    with pytest.raises(
        TypeError,
        match="special_rules must contain only ScenarioRule values.",
    ):
        ScenarioDefinition(
            id="HOLD_GROUND",
            name="Hold Ground",
            pool=ScenarioPool.MAELSTROM_OF_BATTLE,
            deployment_type=DeploymentType.MAELSTROM,
            termination_type=TerminationType.BROKEN_RANDOM,
            special_rules=("maelstrom_of_battle",),
        )

def test_scenario_definition_defaults_to_no_strategic_demands():
    scenario = ScenarioDefinition(
        id="DOMINATION",
        name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    )

    assert scenario.strategic_demands == ()


def test_scenario_definition_stores_multiple_strategic_demands():
    scenario = ScenarioDefinition(
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
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=0.5,
            ),
        ),
    )

    assert scenario.strategic_demands == (
        ScenarioDemand(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            intensity=1.0,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.5,
        ),
    )


def test_scenario_definition_rejects_invalid_strategic_demand_type():
    with pytest.raises(
        TypeError,
        match=(
            "strategic_demands must contain only "
            "ScenarioDemand values."
        ),
    ):
        ScenarioDefinition(
            id="DOMINATION",
            name="Domination",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
            strategic_demands=("distributed_control",),
        )


def test_scenario_definition_rejects_duplicate_strategic_dimensions():
    with pytest.raises(
        ValueError,
        match=(
            "ScenarioDefinition cannot contain duplicate "
            "strategic demand dimensions."
        ),
    ):
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
                ScenarioDemand(
                    dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                    intensity=0.5,
                ),
            ),
        )