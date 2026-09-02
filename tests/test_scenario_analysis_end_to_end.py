from army import Army
from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from faction import Faction
from optimiser_candidate import OptimiserCandidate
from profiles import Profile
from scenario_analysis_builder import (
    build_scenario_analysis_results_from_candidate,
)
from scenario_analysis_report import (
    build_scenario_analysis_report,
)


def test_scenario_analysis_runs_end_to_end():
    profile = Profile(
        id="SCENARIO_ANALYSIS_E2E",
        name="Scenario Analysis End To End Model",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=1,
    )

    army = Army()

    army.add_profile(
        profile,
        quantity=1,
    )

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=faction,
        profiles=[profile],
    )

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    candidate = OptimiserCandidate(
        army=army,
    )

    results = build_scenario_analysis_results_from_candidate(
        candidate=candidate,
        army_list=army_list,
        key_profile=profile,
        combat_benchmark=combat_benchmark,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    assert len(results) == 24

    assert len(
        {
            result.scenario_id
            for result in results
        }
    ) == 24

    assert all(
        0.0 <= result.score <= 1.0
        for result in results
    )

    assert all(
        result.demands
        for result in results
    )

    report = build_scenario_analysis_report(
        results,
    )

    assert "Top Scenarios" in report
    assert "Bottom Scenarios" in report

    top_section, bottom_section = report.split(
        "Bottom Scenarios",
    )

    top_lines = tuple(
        line
        for line in top_section.splitlines()
        if " - " in line
    )

    bottom_lines = tuple(
        line
        for line in bottom_section.splitlines()
        if " - " in line
    )

    assert len(top_lines) == 5
    assert len(bottom_lines) == 5