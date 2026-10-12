"""D4 checks: mechanical facts cannot silently become rated output."""
import pytest

from army import Army
from profiles import Profile
from mobility_integration_contract import build_mobility_integration_contract


def make_army(*, move=6, base=25, points=20, count=2):
    army = Army()
    army.add_profile(Profile(
        id="TEST", name="Test", points=points, movement=move,
        base_size_mm=base, fight=3, shooting="4+", strength=3,
        defence=4, attacks=1, wounds=1, courage="6+", intelligence="7+",
        might=0, will=0, fate=0, max_in_army=0,
    ), quantity=count)
    return army


def test_contract_exposes_physical_measure_and_not_dashboard_score():
    c = build_mobility_integration_contract(make_army())
    assert c.open_ground.value == pytest.approx(6)
    assert c.dashboard_score is None
    assert c.scenario_score is None


def test_contract_marks_calibration_pending():
    c = build_mobility_integration_contract(make_army())
    assert c.calibration_status == "pending"
    assert c.open_ground.evidence_status == "diagnostic_validated_not_calibrated"


def test_open_and_difficult_measures_have_explicit_units_and_dependencies():
    c = build_mobility_integration_contract(make_army())
    assert c.open_ground.unit == c.difficult_terrain.unit == "movement_accessibility_index"
    assert "terrain_movement" in c.difficult_terrain.dependencies
    assert c.open_ground.aggregation == "mean_per_fielded_model"


def test_legacy_metric_has_distinct_id_and_dependency():
    c = build_mobility_integration_contract(make_army())
    assert c.legacy_comparator.metric_id.startswith("mobility.legacy.")
    assert "army_manoeuvrability" in c.legacy_comparator.dependencies
    assert "comparison only" in c.legacy_comparator.assumptions[0]


def test_model_count_affects_count_not_identical_model_mean():
    a = build_mobility_integration_contract(make_army(count=1))
    b = build_mobility_integration_contract(make_army(count=4))
    assert a.open_ground.value == pytest.approx(b.open_ground.value)
    assert a.model_count == 1 and b.model_count == 4


def test_base_size_penalty_remains_in_authoritative_open_measure():
    a = build_mobility_integration_contract(make_army(base=25))
    b = build_mobility_integration_contract(make_army(base=60))
    assert a.open_ground.value > b.open_ground.value


def test_empty_army_has_no_score_or_fabricated_reposition():
    c = build_mobility_integration_contract(Army())
    assert c.open_ground.value == 0
    assert c.difficult_terrain.value == 0
    assert c.potential_anchor_pairs == 0
    assert c.dashboard_score is None
