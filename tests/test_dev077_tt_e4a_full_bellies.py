"""DEV-077-TT-E4A: Full Bellies must affect real army resource totals."""
import pytest
from test_dev077_tt_e2_real_builder_service import real_army, PROFILES


@pytest.mark.parametrize("resource", ("might", "will", "fate"))
def test_purchased_full_bellies_raises_runtime_resource_totals_to_nine(resource):
    definition, army, _ = real_army(("Full Bellies",))
    assert getattr(army, f"total_{resource}")() == 9
    assert all(entry.get_attribute(resource) == 3 for entry in army.entries)
    assert army.total_points() == 450


def test_without_full_bellies_remains_original_values():
    _, bare, _ = real_army(())
    assert (bare.total_might(), bare.total_will(), bare.total_fate()) == (3, 3, 3)
    assert all(not hasattr(entry, "starting_resource_overrides") for entry in bare.entries)


def test_real_seven_hundred_point_roster_uses_nine_each():
    upgrades = (
        "Nothing like a warm fire", "Dominant presence",
        "Tasty Livestock", "Troll Cunning", "Full Bellies",
        "Bowl them over",
    )
    _, army, _ = real_army(upgrades)
    assert army.total_points() == 700
    assert army.purchase_points == 300
    assert (army.total_might(), army.total_will(), army.total_fate()) == (9, 9, 9)
    assert len(army.fielded_models()) == 3


def test_canonical_profiles_unmodified_and_unupgraded_roster_unaffected():
    _, bought, _ = real_army(("Full Bellies",))
    assert bought.total_might() == 9
    assert (PROFILES["TT_BILL"].might,PROFILES["TT_BILL"].will,PROFILES["TT_BILL"].fate) == (1,1,1)
    _, bare, _ = real_army(())
    assert bare.total_might() == 3


def test_analysis_metrics_resource_density_sees_effective_totals():
    _, bought, _ = real_army(("Full Bellies",))
    metrics = bought.analysis_metrics()
    assert metrics.might_density == pytest.approx(9 / 450 * 100)
    assert metrics.will_density == pytest.approx(9 / 450 * 100)
    assert metrics.fate_density == pytest.approx(9 / 450 * 100)


def test_desktop_summary_reads_effective_resource_totals():
    from desktop_analysis_view_model import build_desktop_analysis_view_model
    from types import SimpleNamespace
    definition, army, _ = real_army(("Full Bellies",))
    result = {
        "definition": definition, "army": army,
        "analysis": {"validation_errors": [], "metric_assessments": (),
                     "battlefield_assessments":SimpleNamespace(strengths=(),weaknesses=())},
        "scenario_analysis_results": None, "evidence_records": (),
    }
    view = build_desktop_analysis_view_model(result)
    assert (view["might"], view["will"], view["fate"]) == (9, 9, 9)
