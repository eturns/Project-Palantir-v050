from siege_engine_profile_loader import (
    load_siege_engine_profiles,
)


def test_loads_dale_windlance_from_production_data():
    profiles = load_siege_engine_profiles()

    windlance = profiles["DALE_WINDLANCE"]

    assert windlance.name == "Windlance"
    assert windlance.points == 70
    assert windlance.range_min == 6
    assert windlance.range_max == 60
    assert windlance.strength == 10
    assert windlance.defence == 10
    assert windlance.wounds == 3
    assert windlance.base_size_mm == 50
    assert windlance.size == "SMALL"