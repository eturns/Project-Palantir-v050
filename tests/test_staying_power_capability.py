import pytest
from army import Army
from staying_power_capability import (
    calculate_staying_power,
    calculate_staying_power_from_profile,
    calculate_army_staying_power,
)
from combat_benchmark import CombatBenchmark
from profiles import Profile

def test_staying_power_is_equal_weight_average():
    result = calculate_staying_power(
        defensive_combat=0.8,
        wound_capacity=0.6,
    )

    assert result == pytest.approx(0.7)


def test_staying_power_is_one_when_both_inputs_are_one():
    result = calculate_staying_power(
        defensive_combat=1.0,
        wound_capacity=1.0,
    )

    assert result == 1.0


def test_staying_power_is_zero_when_both_inputs_are_zero():
    result = calculate_staying_power(
        defensive_combat=0.0,
        wound_capacity=0.0,
    )

    assert result == 0.0


@pytest.mark.parametrize(
    "defensive_combat, wound_capacity",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_staying_power_rejects_values_outside_zero_to_one(
    defensive_combat,
    wound_capacity,
):
    with pytest.raises(
        ValueError,
        match="staying power inputs must be between 0.0 and 1.0.",
    ):
        calculate_staying_power(
            defensive_combat=defensive_combat,
            wound_capacity=wound_capacity,
        )


@pytest.mark.parametrize(
    "defensive_combat, wound_capacity",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_staying_power_rejects_non_numeric_inputs(
    defensive_combat,
    wound_capacity,
):
    with pytest.raises(
        TypeError,
        match="staying power inputs must be int or float.",
    ):
        calculate_staying_power(
            defensive_combat=defensive_combat,
            wound_capacity=wound_capacity,
        )

def test_staying_power_from_profile_uses_defence_and_wounds():
    profile = Profile(
        id="TEST",
        name="Test",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    result = calculate_staying_power_from_profile(
        profile=profile,
        benchmark=benchmark,
    )

    assert 0.0 <= result <= 1.0
    assert result > 0.5

def test_army_staying_power_is_quantity_weighted_average(
    monkeypatch,
):
    import staying_power_capability

    army = Army()

    durable_profile = Profile(
        id="DURABLE",
        name="Durable",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=3,
    )

    fragile_profile = Profile(
        id="FRAGILE",
        name="Fragile",
        points=10,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=3,
    )

    army.add_profile(
        durable_profile,
        quantity=2,
    )

    army.add_profile(
        fragile_profile,
        quantity=1,
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        staying_power_capability,
        "calculate_staying_power_from_profile",
        lambda profile, benchmark: (
            0.8
            if profile.id == "DURABLE"
            else 0.2
        ),
    )

    result = calculate_army_staying_power(
        army=army,
        benchmark=benchmark,
    )

    assert result == pytest.approx(
        (
            (0.8 * 2)
            + (0.2 * 1)
        ) / 3
    )

def test_army_staying_power_is_zero_for_empty_army():
    army = Army()

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    result = calculate_army_staying_power(
        army=army,
        benchmark=benchmark,
    )

    assert result == 0.0