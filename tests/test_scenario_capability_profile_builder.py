from army import Army
from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from faction import Faction
from profiles import Profile
from scenario_capability import ScenarioCapability
from scenario_capability_profile_builder import (
    build_scenario_capability_profile,
)
from scenario_demand import StrategicDemand


def test_builder_returns_all_supported_capabilities_and_omits_object_interaction(
    monkeypatch,
):
    import scenario_capability_profile_builder

    army = Army()

    key_profile = Profile(
        id="KEY",
        name="Key Model",
        points=100,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=1,
    )

    army.add_profile(
        key_profile,
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
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    supported_dimensions = (
        StrategicDemand.DISTRIBUTED_CONTROL,
        StrategicDemand.CONCENTRATED_CONTROL,
        StrategicDemand.MOBILITY,
        StrategicDemand.PROJECTION,
        StrategicDemand.ATTRITION_OUTPUT,
        StrategicDemand.KEY_MODEL_PRESSURE,
        StrategicDemand.KEY_MODEL_PRESERVATION,
        StrategicDemand.STATE_RESILIENCE,
        StrategicDemand.DEPLOYMENT_RECOVERY,
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_distributed_control_from_profiles",
        lambda profiles, benchmark_presence: ScenarioCapability(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_concentrated_control_from_army",
        lambda army, benchmark_presence, combat_benchmark,
        benchmark_combat_capability: ScenarioCapability(
            dimension=StrategicDemand.CONCENTRATED_CONTROL,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_mobility_capability_from_army",
        lambda army, benchmark_manoeuvrability: ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_projection_capability_from_army",
        lambda army, army_list: ScenarioCapability(
            dimension=StrategicDemand.PROJECTION,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_attrition_output_capability_from_army",
        lambda army, combat_benchmark,
        benchmark_combat_capability: ScenarioCapability(
            dimension=StrategicDemand.ATTRITION_OUTPUT,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_key_model_pressure_from_army",
        lambda army, army_list, combat_benchmark,
        benchmark_combat_capability: ScenarioCapability(
            dimension=StrategicDemand.KEY_MODEL_PRESSURE,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_key_model_preservation_from_profile",
        lambda profile, benchmark, benchmark_fate: ScenarioCapability(
            dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_state_resilience_from_army",
        lambda army, benchmark: ScenarioCapability(
            dimension=StrategicDemand.STATE_RESILIENCE,
            value=0.5,
        ),
    )

    monkeypatch.setattr(
        scenario_capability_profile_builder,
        "calculate_deployment_recovery_from_army",
        lambda army, benchmark,
        benchmark_manoeuvrability: ScenarioCapability(
            dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
            value=0.5,
        ),
    )

    profile = build_scenario_capability_profile(
        army=army,
        army_list=army_list,
        key_profile=key_profile,
        combat_benchmark=benchmark,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    assert tuple(
        capability.dimension
        for capability in profile.capabilities
    ) == supported_dimensions

    assert profile.has_capability(
        StrategicDemand.OBJECT_INTERACTION,
    ) is False

def test_builder_runs_real_capability_pipeline():
    army = Army()

    profile = Profile(
        id="REAL_TEST",
        name="Real Test Model",
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

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    result = build_scenario_capability_profile(
        army=army,
        army_list=army_list,
        key_profile=profile,
        combat_benchmark=benchmark,
        benchmark_presence=10.0,
        benchmark_manoeuvrability=1.0,
        benchmark_combat_capability=0.5,
        benchmark_fate=4.0,
    )

    assert len(result.capabilities) == 9

    for capability in result.capabilities:
        assert 0.0 <= capability.value <= 1.0

    assert result.has_capability(
        StrategicDemand.OBJECT_INTERACTION,
    ) is False