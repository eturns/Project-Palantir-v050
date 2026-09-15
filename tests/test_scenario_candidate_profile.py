from optimiser_candidate import OptimiserCandidate
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)
from scenario_context import ScenarioContext
from resurrection_config import ResurrectionConfig

def test_scenario_candidate_profile_uses_candidate_army():
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    captured = {}

    def fake_builder(
        *,
        army,
        **kwargs,
    ):
        captured["army"] = army
        return "SCENARIO_PROFILE"

    result = build_scenario_capability_profile_from_candidate(
        candidate=candidate,
        profile_builder=fake_builder,
    )

    assert captured["army"] == "TEST_ARMY"
    assert result == "SCENARIO_PROFILE"


def test_scenario_candidate_profile_passes_builder_inputs():
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    captured = {}

    def fake_profile_builder(
        *,
        army,
        context,
        preservation_profile,
        resurrection_config,
    ):
        captured.update(
            {
                "army": army,
                "context": context,
                "preservation_profile": preservation_profile,
                "resurrection_config": resurrection_config,
            }
        )

        return "SCENARIO_PROFILE"

    context = ScenarioContext(
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    result = build_scenario_capability_profile_from_candidate(
        candidate=candidate,
        context=context,
        preservation_profile="PRESERVATION_PROFILE",
        resurrection_config=ResurrectionConfig(
            resurrection_capable_models=1,
            starting_models=2,
            resilience_weight=0.5,
        ),
        profile_builder=fake_profile_builder,
    )

    assert captured == {
        "army": candidate.army,
        "context": context,
        "preservation_profile": "PRESERVATION_PROFILE",
        "resurrection_config": ResurrectionConfig(
            resurrection_capable_models=1,
            starting_models=2,
            resilience_weight=0.5,
        ),
    }

    assert result == "SCENARIO_PROFILE"

def test_scenario_candidate_profile_uses_default_builder(monkeypatch):
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    captured = {}

    def fake_default_builder(
        *,
        army,
        context,
        preservation_profile,
        resurrection_config,
    ):
        captured["army"] = army
        captured["context"] = context
        return "DEFAULT_PROFILE"

    monkeypatch.setattr(
        "scenario_candidate_profile.build_scenario_capability_profile",
        fake_default_builder,
    )

    context = ScenarioContext(
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    result = build_scenario_capability_profile_from_candidate(
        candidate=candidate,
        context=context,
    )

    assert captured["army"] == "TEST_ARMY"
    assert result == "DEFAULT_PROFILE"