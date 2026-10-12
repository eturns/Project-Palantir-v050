"""DEV-077S-I2-D-C2 aggregation contract regression tests."""
import pytest

from army import Army
from profiles import Profile
from army_mobility_aggregation import aggregate_army_mobility


def profile(name, *, movement=6, base=25, points=20):
    return Profile(
        id=name, name=name, points=points, movement=movement, base_size_mm=base,
        fight=3, shooting="4+", strength=3, defence=4, attacks=1,
        wounds=1, courage="6+", intelligence="7+", might=0, will=0,
        fate=0, max_in_army=0,
    )


def test_empty_army_reports_zero_without_division():
    result = aggregate_army_mobility(Army())
    assert (result.model_count, result.army_points) == (0, 0)
    assert result.average_open_ground == result.open_ground_per_100_points == 0
    assert result.reposition_requires_context is False


def test_quantity_weighted_average_and_total_remain_distinct():
    army = Army()
    army.add_profile(profile("SLOW", movement=6), quantity=2)
    army.add_profile(profile("FAST", movement=10), quantity=1)
    result = aggregate_army_mobility(army)
    assert result.model_count == 3
    assert result.army_points == 60
    assert result.total_open_ground == pytest.approx(22)
    assert result.average_open_ground == pytest.approx(22 / 3)
    assert result.total_difficult_terrain == pytest.approx(11)
    assert result.average_difficult_terrain == pytest.approx(11 / 3)
    assert result.open_ground_per_100_points == pytest.approx(22 * 100 / 60)
    assert result.terrain_retention == pytest.approx(.5)


def test_base_accessibility_penalty_is_retained():
    army = Army()
    army.add_profile(profile("SMALL", base=25), quantity=1)
    army.add_profile(profile("LARGE", base=60), quantity=1)
    result = aggregate_army_mobility(army)
    assert result.average_open_ground < 6.0
    assert result.total_open_ground < 12.0


def test_more_identical_models_preserve_average_but_increase_total():
    one = Army()
    one.add_profile(profile("A"), quantity=1)
    many = Army()
    many.add_profile(profile("B"), quantity=3)
    a, b = aggregate_army_mobility(one), aggregate_army_mobility(many)
    assert a.average_open_ground == pytest.approx(b.average_open_ground)
    assert b.total_open_ground == pytest.approx(a.total_open_ground * 3)
    assert a.open_ground_per_100_points == pytest.approx(b.open_ground_per_100_points)


def test_points_cost_changes_efficiency_not_raw_movement():
    cheap = Army()
    cheap.add_profile(profile("CHEAP", points=10))
    expensive = Army()
    expensive.add_profile(profile("EXPENSIVE", points=30))
    a, b = aggregate_army_mobility(cheap), aggregate_army_mobility(expensive)
    assert a.average_open_ground == b.average_open_ground
    assert a.open_ground_per_100_points == pytest.approx(3 * b.open_ground_per_100_points)


def test_no_blended_or_normalised_score_is_claimed():
    army = Army()
    army.add_profile(profile("SINGLE"))
    result = aggregate_army_mobility(army)
    assert result.average_open_ground == pytest.approx(6)
    assert result.average_difficult_terrain == pytest.approx(3)
    assert not hasattr(result, "normalised_mobility")
    assert not hasattr(result, "combined_mobility")
