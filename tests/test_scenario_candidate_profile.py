from optimiser_candidate import OptimiserCandidate
from scenario_candidate_profile import (
    build_scenario_capability_profile_from_candidate,
)


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

    def fake_builder(
        *,
        army,
        army_list,
        key_profile,
        combat_benchmark,
        benchmark_presence,
        benchmark_manoeuvrability,
        benchmark_combat_capability,
        benchmark_fate,
        resurrection_config,
    ):
        captured.update(
            {
                "army": army,
                "army_list": army_list,
                "key_profile": key_profile,
                "combat_benchmark": combat_benchmark,
                "benchmark_presence": benchmark_presence,
                "benchmark_manoeuvrability": benchmark_manoeuvrability,
                "benchmark_combat_capability": benchmark_combat_capability,
                "benchmark_fate": benchmark_fate,
                "resurrection_config": resurrection_config,
            }
        )

        return "SCENARIO_PROFILE"

    result = build_scenario_capability_profile_from_candidate(
        candidate=candidate,
        profile_builder=fake_builder,
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
        resurrection_config={
            "test": True,
        },
    )

    assert captured == {
        "army": "TEST_ARMY",
        "army_list": "ARMY_LIST",
        "key_profile": "KEY_PROFILE",
        "combat_benchmark": "COMBAT_BENCHMARK",
        "benchmark_presence": 10,
        "benchmark_manoeuvrability": 20,
        "benchmark_combat_capability": 30,
        "benchmark_fate": 40,
        "resurrection_config": {
            "test": True,
        },
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
        army_list,
        key_profile,
        combat_benchmark,
        benchmark_presence,
        benchmark_manoeuvrability,
        benchmark_combat_capability,
        benchmark_fate,
        resurrection_config,
    ):
        captured["army"] = army
        return "DEFAULT_PROFILE"

    monkeypatch.setattr(
        "scenario_candidate_profile.build_scenario_capability_profile",
        fake_default_builder,
    )

    result = build_scenario_capability_profile_from_candidate(
        candidate=candidate,
        army_list="ARMY_LIST",
        key_profile="KEY_PROFILE",
        combat_benchmark="COMBAT_BENCHMARK",
        benchmark_presence=10,
        benchmark_manoeuvrability=20,
        benchmark_combat_capability=30,
        benchmark_fate=40,
        resurrection_config=None,
    )

    assert captured["army"] == "TEST_ARMY"
    assert result == "DEFAULT_PROFILE"