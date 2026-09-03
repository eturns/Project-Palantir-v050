from scenario_analysis_builder import (
    build_scenario_analysis_results,
    build_scenario_analysis_results_from_profile,
)
from scenario_capability import (
    ScenarioCapability,
    ScenarioCapabilityProfile,
)
from scenario_definition import ScenarioPool
from scenario_demand import StrategicDemand
from optimiser_candidate import OptimiserCandidate
from scenario_analysis_builder import (
    build_scenario_analysis_results,
    build_scenario_analysis_results_from_candidate,
    build_scenario_analysis_results_from_profile,
    rank_scenario_analysis_results,
    scenario_analysis_extremes,
)
from scenario_analysis_result import ScenarioAnalysisResult

def test_build_scenario_analysis_results_returns_all_24_scenarios():
    results = build_scenario_analysis_results(
        scenario_scores=(
            (
                "DOMINATION",
                "Domination",
                ScenarioPool.HOLD_OBJECTIVE,
                0.8,
            ),
            (
                "TO_THE_DEATH",
                "To the Death!",
                ScenarioPool.KILL_THE_ENEMY,
                0.6,
            ),
        ),
    )

    assert len(results) == 2

    assert results[0].scenario_id == "DOMINATION"
    assert results[0].scenario_name == "Domination"
    assert results[0].pool == ScenarioPool.HOLD_OBJECTIVE
    assert results[0].score == 0.8

    assert results[1].scenario_id == "TO_THE_DEATH"
    assert results[1].scenario_name == "To the Death!"
    assert results[1].pool == ScenarioPool.KILL_THE_ENEMY
    assert results[1].score == 0.6

def test_build_scenario_analysis_results_from_profile_returns_all_24_scenarios():
    capability_profile = ScenarioCapabilityProfile(
    capabilities=(
        ScenarioCapability(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            value=0.8,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.CONCENTRATED_CONTROL,
            value=0.7,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=0.9,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.PROJECTION,
            value=0.4,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.ATTRITION_OUTPUT,
            value=0.6,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.KEY_MODEL_PRESSURE,
            value=0.5,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
            value=0.3,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.STATE_RESILIENCE,
            value=0.65,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
            value=0.775,
        ),
    ),
)

    results = build_scenario_analysis_results_from_profile(
        capability_profile,
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

def test_build_scenario_analysis_results_from_candidate_uses_candidate_profile_path(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    capability_profile = object()

    expected_results = (
        "RESULT_A",
        "RESULT_B",
    )

    captured = {}

    def fake_profile_builder(
        candidate,
        **kwargs,
    ):
        captured["candidate"] = candidate
        captured["kwargs"] = kwargs
        return capability_profile

    def fake_result_builder(
        profile,
        *,
        scenario_capability_overrides=None,
    ):
        captured["profile"] = profile
        captured["scenario_capability_overrides"] = (
            scenario_capability_overrides
        )
        return expected_results

    monkeypatch.setattr(
        "scenario_analysis_builder."
        "build_scenario_capability_profile_from_candidate",
        fake_profile_builder,
    )

    monkeypatch.setattr(
        "scenario_analysis_builder."
        "build_scenario_analysis_results_from_profile",
        fake_result_builder,
    )

    result = build_scenario_analysis_results_from_candidate(
        candidate=candidate,
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        preservation_profile="PRESERVATION_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
        resurrection_config={
            "test": True,
        },
    )

    assert result is expected_results

    assert captured["candidate"] is candidate

    assert captured["profile"] is capability_profile

    assert captured["scenario_capability_overrides"] == {}

    assert captured["kwargs"] == {
        "army_list": "ARMY_LIST",
        "key_profile": "KEY_PROFILE",
        "preservation_profile": "PRESERVATION_PROFILE",
        "combat_benchmark": "COMBAT_BENCHMARK",
        "benchmark_presence": 10,
        "benchmark_manoeuvrability": 20,
        "benchmark_combat_capability": 30,
        "benchmark_fate": 40,
        "resurrection_config": {
            "test": True,
        },
    }

def test_rank_scenario_analysis_results_orders_best_to_worst():
    results = (
        ScenarioAnalysisResult(
            scenario_id="LOW",
            scenario_name="Low",
            pool=ScenarioPool.UNIQUE,
            score=0.2,
        ),
        ScenarioAnalysisResult(
            scenario_id="HIGH",
            scenario_name="High",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.9,
        ),
        ScenarioAnalysisResult(
            scenario_id="MID",
            scenario_name="Mid",
            pool=ScenarioPool.OBJECT,
            score=0.5,
        ),
    )

    ranked = rank_scenario_analysis_results(
        results,
    )

    assert tuple(
        result.scenario_id
        for result in ranked
    ) == (
        "HIGH",
        "MID",
        "LOW",
    )

def test_scenario_analysis_extremes_returns_top_and_bottom_results():
    results = tuple(
        ScenarioAnalysisResult(
            scenario_id=f"SCENARIO_{index}",
            scenario_name=f"Scenario {index}",
            pool=ScenarioPool.UNIQUE,
            score=index / 10,
        )
        for index in range(10)
    )

    ranked = rank_scenario_analysis_results(
        results,
    )

    top, bottom = scenario_analysis_extremes(
        ranked,
        count=3,
    )

    assert tuple(
        result.scenario_id
        for result in top
    ) == (
        "SCENARIO_9",
        "SCENARIO_8",
        "SCENARIO_7",
    )

    assert tuple(
        result.scenario_id
        for result in bottom
    ) == (
        "SCENARIO_2",
        "SCENARIO_1",
        "SCENARIO_0",
    )

def test_build_scenario_analysis_results_from_profile_populates_demand_analysis():
    capability_profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                value=0.8,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.CONCENTRATED_CONTROL,
                value=0.7,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.9,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.PROJECTION,
                value=0.4,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.ATTRITION_OUTPUT,
                value=0.6,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.KEY_MODEL_PRESSURE,
                value=0.5,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
                value=0.3,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.STATE_RESILIENCE,
                value=0.65,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                value=0.775,
            ),
        ),
    )

    results = build_scenario_analysis_results_from_profile(
        capability_profile,
    )

    domination = next(
        result
        for result in results
        if result.scenario_id == "DOMINATION"
    )

    assert len(domination.demands) == 1

    assert domination.demands[0].dimension == (
        StrategicDemand.DISTRIBUTED_CONTROL
    )

    assert domination.demands[0].capability == 0.8
    assert domination.demands[0].intensity == 1.0

def test_fog_of_war_can_override_key_model_preservation():
    capability_profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                value=0.8,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.CONCENTRATED_CONTROL,
                value=0.7,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.9,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.PROJECTION,
                value=0.4,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.ATTRITION_OUTPUT,
                value=0.6,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.KEY_MODEL_PRESSURE,
                value=0.5,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
                value=0.3,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.STATE_RESILIENCE,
                value=0.65,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
                value=0.775,
            ),
        ),
    )

    results = build_scenario_analysis_results_from_profile(
        capability_profile,
        scenario_capability_overrides={
            "FOG_OF_WAR": {
                StrategicDemand.KEY_MODEL_PRESERVATION: 0.8,
            },
        },
    )

    fog_of_war = next(
        result
        for result in results
        if result.scenario_id == "FOG_OF_WAR"
    )

    lead_from_the_front = next(
        result
        for result in results
        if result.scenario_id == "LEAD_FROM_THE_FRONT"
    )

    fog_preservation = next(
        demand
        for demand in fog_of_war.demands
        if demand.dimension
        is StrategicDemand.KEY_MODEL_PRESERVATION
    )

    lead_preservation = next(
        demand
        for demand in lead_from_the_front.demands
        if demand.dimension
        is StrategicDemand.KEY_MODEL_PRESERVATION
    )

    assert fog_preservation.capability == 0.8
    assert lead_preservation.capability == 0.3

def test_candidate_analysis_uses_fog_of_war_preservation_override(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    capability_profile = object()

    leader_profile = object()
    fog_profile = object()

    expected_results = (
        "RESULT_A",
        "RESULT_B",
    )

    captured = {}

    def fake_profile_builder(
        candidate,
        **kwargs,
    ):
        return capability_profile

    def fake_select_fog_profile(
        *,
        army,
        leader_profile,
        combat_benchmark,
        benchmark_fate,
    ):
        captured["selector"] = {
            "army": army,
            "leader_profile": leader_profile,
            "combat_benchmark": combat_benchmark,
            "benchmark_fate": benchmark_fate,
        }

        return fog_profile

    def fake_preservation_calculator(
        *,
        profile,
        benchmark,
        benchmark_fate,
        army=None,
        army_list=None,
    ):
        assert profile is fog_profile
        assert benchmark == "COMBAT_BENCHMARK"
        assert benchmark_fate == 40

        captured["preservation_army"] = army
        captured["preservation_army_list"] = army_list

        class Result:
            value = 0.8

        return Result()

    def fake_result_builder(
        profile,
        *,
        scenario_capability_overrides=None,
    ):
        captured["profile"] = profile
        captured["overrides"] = (
            scenario_capability_overrides
        )

        return expected_results

    monkeypatch.setattr(
        "scenario_analysis_builder."
        "build_scenario_capability_profile_from_candidate",
        fake_profile_builder,
    )

    monkeypatch.setattr(
        "scenario_analysis_builder."
        "select_fog_of_war_preservation_profile",
        fake_select_fog_profile,
    )

    monkeypatch.setattr(
        "scenario_analysis_builder."
        "calculate_key_model_preservation_from_profile",
        fake_preservation_calculator,
    )

    monkeypatch.setattr(
        "scenario_analysis_builder."
        "build_scenario_analysis_results_from_profile",
        fake_result_builder,
    )

    result = build_scenario_analysis_results_from_candidate(
        candidate=candidate,
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        leader_profile=leader_profile,
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    assert result is expected_results

    assert captured["selector"] == {
        "army": "TEST_ARMY",
        "leader_profile": leader_profile,
        "combat_benchmark": "COMBAT_BENCHMARK",
        "benchmark_fate": 40,
    }

    assert captured["profile"] is capability_profile

    assert captured["overrides"] == {
        "FOG_OF_WAR": {
            StrategicDemand.KEY_MODEL_PRESERVATION: 0.8,
        },
    }
    assert captured["preservation_army"] == "TEST_ARMY"

    assert captured["preservation_army_list"] == "ARMY_LIST"