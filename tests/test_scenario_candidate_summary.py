from optimiser_candidate import OptimiserCandidate
from scenario_candidate_summary import (
    build_scenario_pool_fit_summary_from_candidate,
)
from scenario_context import ScenarioContext
from resurrection_config import ResurrectionConfig

def test_scenario_candidate_summary_builds_profile_then_summary():
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    captured = {}

    def fake_profile_builder(
        *,
        candidate,
        **kwargs,
    ):
        captured["profile_candidate"] = candidate
        return "SCENARIO_PROFILE"

    def fake_summary_builder(
        capability_profile,
    ):
        captured["summary_profile"] = capability_profile
        return "SCENARIO_SUMMARY"

    result = build_scenario_pool_fit_summary_from_candidate(
        candidate=candidate,
        profile_builder=fake_profile_builder,
        summary_builder=fake_summary_builder,
    )

    assert captured["profile_candidate"] is candidate
    assert captured["summary_profile"] == "SCENARIO_PROFILE"
    assert result == "SCENARIO_SUMMARY"

def test_scenario_candidate_summary_passes_profile_builder_inputs():
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    captured = {}

    def fake_profile_builder(
        *,
        candidate,
        context,
        resurrection_config,
    ):
        captured.update(
            {
                "candidate": candidate,
                "context": context,
                "resurrection_config": resurrection_config,
            }
        )

        return "SCENARIO_PROFILE"

    def fake_summary_builder(
        capability_profile,
    ):
        return "SCENARIO_SUMMARY"

    context = ScenarioContext(
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
    )

    result = build_scenario_pool_fit_summary_from_candidate(
        candidate=candidate,
        context=context,
        resurrection_config=ResurrectionConfig(
            resurrection_capable_models=1,
            starting_models=2,
            resilience_weight=0.5,
        ),
        profile_builder=fake_profile_builder,
        summary_builder=fake_summary_builder,
    )

    assert captured == {
        "candidate": candidate,
        "context": context,
        "resurrection_config": ResurrectionConfig(
            resurrection_capable_models=1,
            starting_models=2,
            resilience_weight=0.5,
        ),
    }

    assert result == "SCENARIO_SUMMARY"

def test_scenario_candidate_summary_uses_default_builders(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army="TEST_ARMY",
    )

    captured = {}

    def fake_default_profile_builder(
        *,
        candidate,
        **kwargs,
    ):
        captured["candidate"] = candidate
        return "SCENARIO_PROFILE"

    def fake_default_summary_builder(
        capability_profile,
    ):
        captured["profile"] = capability_profile
        return "SCENARIO_SUMMARY"

    monkeypatch.setattr(
        "scenario_candidate_summary."
        "build_scenario_capability_profile_from_candidate",
        fake_default_profile_builder,
    )

    monkeypatch.setattr(
        "scenario_candidate_summary."
        "build_official_scenario_pool_fit_summary_from_profile",
        fake_default_summary_builder,
    )

    result = build_scenario_pool_fit_summary_from_candidate(
        candidate=candidate,
    )

    assert captured["candidate"] is candidate
    assert captured["profile"] == "SCENARIO_PROFILE"
    assert result == "SCENARIO_SUMMARY"