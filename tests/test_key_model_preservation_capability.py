import pytest
from combat_benchmark import CombatBenchmark
from profiles import Profile
from key_model_preservation_capability import (
    calculate_key_model_preservation_capability,
    calculate_key_model_preservation_from_profile,
    calculate_protective_resources_from_army_profile,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand
from army import Army
from resource_conversion import ResourceConversion
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from army_list import ArmyList
from army_rule import ArmyRule
from faction import Faction

def test_key_model_preservation_is_equal_weight_average():
    result = calculate_key_model_preservation_capability(
        defensive_survivability=0.8,
        protective_resources=0.6,
    )

    assert (
        result.dimension
        == StrategicDemand.KEY_MODEL_PRESERVATION
    )
    assert result.value == pytest.approx(0.7)


def test_key_model_preservation_is_one_when_both_inputs_are_one():
    result = calculate_key_model_preservation_capability(
        defensive_survivability=1.0,
        protective_resources=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
        value=1.0,
    )


def test_key_model_preservation_is_zero_when_both_inputs_are_zero():
    result = calculate_key_model_preservation_capability(
        defensive_survivability=0.0,
        protective_resources=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
        value=0.0,
    )


@pytest.mark.parametrize(
    "defensive_survivability, protective_resources",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_key_model_preservation_rejects_values_outside_zero_to_one(
    defensive_survivability,
    protective_resources,
):
    with pytest.raises(
        ValueError,
        match="capability inputs must be between 0.0 and 1.0.",
    ):
        calculate_key_model_preservation_capability(
            defensive_survivability=defensive_survivability,
            protective_resources=protective_resources,
        )


@pytest.mark.parametrize(
    "defensive_survivability, protective_resources",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_key_model_preservation_rejects_non_numeric_inputs(
    defensive_survivability,
    protective_resources,
):
    with pytest.raises(
        TypeError,
        match="capability inputs must be int or float.",
    ):
        calculate_key_model_preservation_capability(
            defensive_survivability=defensive_survivability,
            protective_resources=protective_resources,
        )

def test_key_model_preservation_from_profile_combines_staying_power_and_fate(
    monkeypatch,
):
    import key_model_preservation_capability

    profile = Profile(
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

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        key_model_preservation_capability,
        "calculate_staying_power_from_profile",
        lambda profile, benchmark: 0.8,
    )

    result = calculate_key_model_preservation_from_profile(
        profile=profile,
        benchmark=benchmark,
        benchmark_fate=4,
    )

    assert (
        result.dimension
        == StrategicDemand.KEY_MODEL_PRESERVATION
    )

    assert result.value == pytest.approx(
        (
            0.8
            + 0.5
        ) / 2
    )

def test_protective_resources_include_legal_will_to_fate_conversion():
    profile_without_conversion = Profile(
        id="NO_CONVERSION",
        name="No Conversion",
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
        might=0,
        will=4,
        fate=0,
        max_in_army=1,
    )

    profile_with_conversion = Profile(
        id="WITH_CONVERSION",
        name="With Conversion",
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
        might=0,
        will=4,
        fate=0,
        max_in_army=1,
        special_resource_conversions=(
            ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            ),
        ),
    )

    army_without_conversion = Army()
    army_without_conversion.add_profile(
        profile_without_conversion,
        quantity=1,
    )

    army_with_conversion = Army()
    army_with_conversion.add_profile(
        profile_with_conversion,
        quantity=1,
    )

    without_conversion = (
        calculate_protective_resources_from_army_profile(
            army=army_without_conversion,
            profile=profile_without_conversion,
            benchmark_fate=4,
        )
    )

    with_conversion = (
        calculate_protective_resources_from_army_profile(
            army=army_with_conversion,
            profile=profile_with_conversion,
            benchmark_fate=4,
        )
    )

    assert without_conversion == 0.0
    assert with_conversion > without_conversion

def test_protective_resources_budget_convertible_will_over_standard_horizon():
    profile = Profile(
        id="CONVERTIBLE_WILL",
        name="Convertible Will",
        points=200,
        movement=6,
        fight=6,
        shooting="4+",
        strength=6,
        defence=8,
        attacks=1,
        wounds=3,
        courage="4+",
        intelligence="4+",
        might=3,
        will=25,
        fate=0,
        max_in_army=1,
        special_resource_conversions=(
            ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            ),
        ),
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=1,
    )

    result = (
        calculate_protective_resources_from_army_profile(
            army=army,
            profile=profile,
            benchmark_fate=4,
        )
    )

    assert result == pytest.approx(1.0)

def test_key_model_preservation_from_profile_uses_army_rule_resource_share(
    monkeypatch,
):
    import key_model_preservation_capability

    profile = Profile(
        id="CONVERTIBLE_KEY",
        name="Convertible Key Model",
        points=200,
        movement=6,
        fight=6,
        shooting="4+",
        strength=6,
        defence=8,
        attacks=1,
        wounds=3,
        courage="4+",
        intelligence="4+",
        might=3,
        will=25,
        fate=0,
        max_in_army=1,
        special_resource_conversions=(
            ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            ),
        ),
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=1,
    )

    army_list = ArmyList(
        id="DG_ROTN",
        name="Rise of the Necromancer",
        faction=Faction(
            id="DOL_GULDUR",
            name="Dol Guldur",
        ),
        army_rules=[
            ArmyRule(
                id="DG_POWER_OF_THE_NECROMANCER",
                name="Power of the Necromancer",
            ),
        ],
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        key_model_preservation_capability,
        "calculate_staying_power_from_profile",
        lambda profile, benchmark: 0.6,
    )

    result = calculate_key_model_preservation_from_profile(
        profile=profile,
        army=army,
        army_list=army_list,
        benchmark=benchmark,
        benchmark_fate=3,
    )

    assert result.value == pytest.approx(
        (
            0.6
            + ((4 / 3) / 3)
        ) / 2
    )

def test_power_of_the_necromancer_reduces_convertible_will_to_one_third():
    profile = Profile(
        id="CASTER",
        name="Caster",
        points=200,
        movement=6,
        fight=6,
        shooting="4+",
        strength=6,
        defence=8,
        attacks=1,
        wounds=3,
        courage="4+",
        intelligence="4+",
        might=3,
        will=25,
        fate=0,
        max_in_army=1,
        special_resource_conversions=(
            ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            ),
        ),
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=1,
    )

    army_list = ArmyList(
        id="DG_ROTN",
        name="Rise of the Necromancer",
        faction=Faction(
            id="DOL_GULDUR",
            name="Dol Guldur",
        ),
        army_rules=[
            ArmyRule(
                id="DG_POWER_OF_THE_NECROMANCER",
                name="Power of the Necromancer",
            ),
        ],
    )

    result = calculate_protective_resources_from_army_profile(
        army=army,
        profile=profile,
        benchmark_fate=3,
        army_list=army_list,
    )

    assert result == pytest.approx(
        (4 / 3) / 3
    )