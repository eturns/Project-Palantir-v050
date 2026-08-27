from scenario_catalogue import (
    OFFICIAL_SCENARIOS,
    get_official_scenario,
    get_official_scenarios,
    get_official_scenarios_by_pool,
)
from scenario_definition import (
    DeploymentType,
    ScenarioPool,
    ScenarioRule,
    TerminationType,
)


def test_official_scenario_catalogue_contains_24_scenarios():
    assert len(OFFICIAL_SCENARIOS) == 24


def test_official_scenario_catalogue_contains_six_pools():
    pools = {
        scenario.pool
        for scenario in OFFICIAL_SCENARIOS
    }

    assert pools == set(ScenarioPool)


def test_each_official_pool_contains_four_scenarios():
    for pool in ScenarioPool:
        scenarios = [
            scenario
            for scenario in OFFICIAL_SCENARIOS
            if scenario.pool is pool
        ]

        assert len(scenarios) == 4


def test_official_scenario_ids_are_unique():
    ids = [
        scenario.id
        for scenario in OFFICIAL_SCENARIOS
    ]

    assert len(ids) == len(set(ids))


def test_official_scenario_names_are_unique():
    names = [
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
    ]

    assert len(names) == len(set(names))


def test_get_official_scenarios_returns_full_catalogue():
    assert get_official_scenarios() == OFFICIAL_SCENARIOS


def test_get_official_scenarios_returns_tuple():
    assert isinstance(
        get_official_scenarios(),
        tuple,
    )

def test_hold_objective_pool_contains_exact_official_scenarios():
    names = {
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is ScenarioPool.HOLD_OBJECTIVE
    }

    assert names == {
        "Domination",
        "Capture & Control",
        "Breakthrough",
        "Stake a Claim",
    }


def test_kill_the_enemy_pool_contains_exact_official_scenarios():
    names = {
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is ScenarioPool.KILL_THE_ENEMY
    }

    assert names == {
        "To the Death!",
        "Lords of Battle",
        "Assassination",
        "Contest of Champions",
    }


def test_maelstrom_of_battle_pool_contains_exact_official_scenarios():
    names = {
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is ScenarioPool.MAELSTROM_OF_BATTLE
    }

    assert names == {
        "Hold Ground",
        "Heirloom of Ages Past",
        "Sites of Power",
        "Command the Battlefield",
    }


def test_object_pool_contains_exact_official_scenarios():
    names = {
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is ScenarioPool.OBJECT
    }

    assert names == {
        "Destroy the Supplies",
        "Retrieval",
        "Seize the Prizes",
        "Treasure Hoard",
    }


def test_manoeuvring_pool_contains_exact_official_scenarios():
    names = {
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is ScenarioPool.MANOEUVRING
    }

    assert names == {
        "Reconnoitre",
        "Storm the Camp",
        "Divide & Conquer",
        "Escort the Wounded",
    }


def test_unique_pool_contains_exact_official_scenarios():
    names = {
        scenario.name
        for scenario in OFFICIAL_SCENARIOS
        if scenario.pool is ScenarioPool.UNIQUE
    }

    assert names == {
        "Fog of War",
        "Clash by Moonlight",
        "Lead from the Front",
        "Convergence",
    }

def test_get_official_scenario_returns_matching_scenario_by_id():
    scenario = get_official_scenario("DOMINATION")

    assert scenario.id == "DOMINATION"
    assert scenario.name == "Domination"
    assert scenario.pool is ScenarioPool.HOLD_OBJECTIVE


def test_get_official_scenario_returns_correct_non_first_scenario():
    scenario = get_official_scenario("CONVERGENCE")

    assert scenario.id == "CONVERGENCE"
    assert scenario.name == "Convergence"
    assert scenario.pool is ScenarioPool.UNIQUE


def test_get_official_scenario_rejects_unknown_id():
    import pytest

    with pytest.raises(
        ValueError,
        match="Unknown official scenario ID: NOT_A_SCENARIO",
    ):
        get_official_scenario("NOT_A_SCENARIO")


def test_get_official_scenario_rejects_blank_id():
    import pytest

    with pytest.raises(
        ValueError,
        match="Scenario ID cannot be blank.",
    ):
        get_official_scenario("")

def test_get_official_scenarios_by_pool_returns_exact_pool_members():
    scenarios = get_official_scenarios_by_pool(
        ScenarioPool.OBJECT,
    )

    assert tuple(
        scenario.name
        for scenario in scenarios
    ) == (
        "Destroy the Supplies",
        "Retrieval",
        "Seize the Prizes",
        "Treasure Hoard",
    )


def test_get_official_scenarios_by_pool_returns_tuple():
    scenarios = get_official_scenarios_by_pool(
        ScenarioPool.UNIQUE,
    )

    assert isinstance(
        scenarios,
        tuple,
    )


def test_get_official_scenarios_by_pool_returns_four_scenarios():
    for pool in ScenarioPool:
        assert len(
            get_official_scenarios_by_pool(pool)
        ) == 4


def test_get_official_scenarios_by_pool_rejects_invalid_pool():
    import pytest

    with pytest.raises(
        TypeError,
        match="pool must be a ScenarioPool.",
    ):
        get_official_scenarios_by_pool(
            "object",
        )       

from scenario_definition import (
    ScenarioPool,
    TerminationType,
)


def test_domination_uses_quarter_strength_termination():
    scenario = get_official_scenario("DOMINATION")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_to_the_death_uses_quarter_strength_termination():
    scenario = get_official_scenario("TO_THE_DEATH")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_hold_ground_uses_broken_random_termination():
    scenario = get_official_scenario("HOLD_GROUND")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_destroy_the_supplies_uses_quarter_strength_termination():
    scenario = get_official_scenario("DESTROY_THE_SUPPLIES")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_reconnoitre_uses_quarter_strength_termination():
    scenario = get_official_scenario("RECONNOITRE")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_fog_of_war_uses_broken_random_termination():
    scenario = get_official_scenario("FOG_OF_WAR")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_capture_and_control_uses_broken_random_termination():
    scenario = get_official_scenario("CAPTURE_AND_CONTROL")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_breakthrough_uses_quarter_strength_termination():
    scenario = get_official_scenario("BREAKTHROUGH")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_stake_a_claim_uses_quarter_strength_termination():
    scenario = get_official_scenario("STAKE_A_CLAIM")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )

def test_lords_of_battle_uses_broken_random_termination():
    scenario = get_official_scenario("LORDS_OF_BATTLE")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_assassination_uses_broken_random_termination():
    scenario = get_official_scenario("ASSASSINATION")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_contest_of_champions_uses_quarter_strength_termination():
    scenario = get_official_scenario("CONTEST_OF_CHAMPIONS")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_heirloom_of_ages_past_uses_quarter_strength_termination():
    scenario = get_official_scenario("HEIRLOOM_OF_AGES_PAST")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_sites_of_power_uses_quarter_strength_termination():
    scenario = get_official_scenario("SITES_OF_POWER")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_command_the_battlefield_uses_quarter_strength_termination():
    scenario = get_official_scenario("COMMAND_THE_BATTLEFIELD")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_retrieval_uses_broken_random_termination():
    scenario = get_official_scenario("RETRIEVAL")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_seize_the_prizes_uses_scenario_specific_termination():
    scenario = get_official_scenario("SEIZE_THE_PRIZES")

    assert (
        scenario.termination_type
        is TerminationType.SCENARIO_SPECIFIC
    )


def test_treasure_hoard_uses_quarter_strength_termination():
    scenario = get_official_scenario("TREASURE_HOARD")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )

def test_storm_the_camp_uses_quarter_strength_termination():
    scenario = get_official_scenario("STORM_THE_CAMP")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_divide_and_conquer_uses_broken_random_termination():
    scenario = get_official_scenario("DIVIDE_AND_CONQUER")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )


def test_escort_the_wounded_uses_quarter_strength_termination():
    scenario = get_official_scenario("ESCORT_THE_WOUNDED")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_clash_by_moonlight_uses_quarter_strength_termination():
    scenario = get_official_scenario("CLASH_BY_MOONLIGHT")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_lead_from_the_front_uses_quarter_strength_termination():
    scenario = get_official_scenario("LEAD_FROM_THE_FRONT")

    assert (
        scenario.termination_type
        is TerminationType.QUARTER_STRENGTH
    )


def test_convergence_uses_broken_random_termination():
    scenario = get_official_scenario("CONVERGENCE")

    assert (
        scenario.termination_type
        is TerminationType.BROKEN_RANDOM
    )

def test_hold_ground_uses_maelstrom_of_battle_rule():
    scenario = get_official_scenario("HOLD_GROUND")

    assert scenario.special_rules == (
        ScenarioRule.MAELSTROM_OF_BATTLE,
    )


def test_lords_of_battle_uses_a_time_of_heroes_rule():
    scenario = get_official_scenario("LORDS_OF_BATTLE")

    assert scenario.special_rules == (
        ScenarioRule.A_TIME_OF_HEROES,
    )


def test_assassination_uses_dark_of_night_rule():
    scenario = get_official_scenario("ASSASSINATION")

    assert scenario.special_rules == (
        ScenarioRule.DARK_OF_NIGHT,
    )


def test_contest_of_champions_uses_a_time_of_heroes_rule():
    scenario = get_official_scenario("CONTEST_OF_CHAMPIONS")

    assert scenario.special_rules == (
        ScenarioRule.A_TIME_OF_HEROES,
    )


def test_heirloom_of_ages_past_uses_maelstrom_of_battle_rule():
    scenario = get_official_scenario("HEIRLOOM_OF_AGES_PAST")

    assert scenario.special_rules == (
        ScenarioRule.MAELSTROM_OF_BATTLE,
    )


def test_sites_of_power_uses_dark_of_night_and_maelstrom_rules():
    scenario = get_official_scenario("SITES_OF_POWER")

    assert scenario.special_rules == (
        ScenarioRule.DARK_OF_NIGHT,
        ScenarioRule.MAELSTROM_OF_BATTLE,
    )


def test_command_the_battlefield_uses_maelstrom_of_battle_rule():
    scenario = get_official_scenario("COMMAND_THE_BATTLEFIELD")

    assert scenario.special_rules == (
        ScenarioRule.MAELSTROM_OF_BATTLE,
    )


def test_clash_by_moonlight_uses_dark_of_night_rule():
    scenario = get_official_scenario("CLASH_BY_MOONLIGHT")

    assert scenario.special_rules == (
        ScenarioRule.DARK_OF_NIGHT,
    )


def test_lead_from_the_front_uses_a_time_of_heroes_rule():
    scenario = get_official_scenario("LEAD_FROM_THE_FRONT")

    assert scenario.special_rules == (
        ScenarioRule.A_TIME_OF_HEROES,
    )

def test_hold_ground_uses_maelstrom_deployment():
    scenario = get_official_scenario("HOLD_GROUND")

    assert (
        scenario.deployment_type
        is DeploymentType.MAELSTROM
    )


def test_heirloom_of_ages_past_uses_maelstrom_deployment():
    scenario = get_official_scenario("HEIRLOOM_OF_AGES_PAST")

    assert (
        scenario.deployment_type
        is DeploymentType.MAELSTROM
    )


def test_sites_of_power_uses_maelstrom_deployment():
    scenario = get_official_scenario("SITES_OF_POWER")

    assert (
        scenario.deployment_type
        is DeploymentType.MAELSTROM
    )


def test_command_the_battlefield_uses_maelstrom_deployment():
    scenario = get_official_scenario("COMMAND_THE_BATTLEFIELD")

    assert (
        scenario.deployment_type
        is DeploymentType.MAELSTROM
    )


def test_reconnoitre_uses_reinforcements_deployment():
    scenario = get_official_scenario("RECONNOITRE")

    assert (
        scenario.deployment_type
        is DeploymentType.REINFORCEMENTS
    )


def test_divide_and_conquer_uses_split_deployment():
    scenario = get_official_scenario("DIVIDE_AND_CONQUER")

    assert (
        scenario.deployment_type
        is DeploymentType.SPLIT
    )


def test_convergence_uses_split_deployment():
    scenario = get_official_scenario("CONVERGENCE")

    assert (
        scenario.deployment_type
        is DeploymentType.SPLIT
    )

def test_all_other_official_scenarios_use_standard_deployment():
    non_standard_ids = {
        "HOLD_GROUND",
        "HEIRLOOM_OF_AGES_PAST",
        "SITES_OF_POWER",
        "COMMAND_THE_BATTLEFIELD",
        "RECONNOITRE",
        "DIVIDE_AND_CONQUER",
        "CONVERGENCE",
    }

    standard_scenarios = tuple(
        scenario
        for scenario in OFFICIAL_SCENARIOS
        if scenario.id not in non_standard_ids
    )

    assert len(standard_scenarios) == 17

    assert all(
        scenario.deployment_type
        is DeploymentType.STANDARD
        for scenario in standard_scenarios
    )

def test_every_official_scenario_uses_valid_canonical_metadata():
    for scenario in OFFICIAL_SCENARIOS:
        assert isinstance(
            scenario.pool,
            ScenarioPool,
        )
        assert isinstance(
            scenario.deployment_type,
            DeploymentType,
        )
        assert isinstance(
            scenario.termination_type,
            TerminationType,
        )
        assert all(
            isinstance(rule, ScenarioRule)
            for rule in scenario.special_rules
        )


def test_every_official_scenario_has_non_blank_identity():
    for scenario in OFFICIAL_SCENARIOS:
        assert scenario.id.strip()
        assert scenario.name.strip()