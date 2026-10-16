"""B8-B focused audit contracts."""
import pytest
from i2i_c3_b8b_mechanical_qualification import (
    expected_option_counts, evaluate_one, audit, CRITICAL_EFFECTS,
)
from i2i_c3_b8a_cohort_intake import FIXTURES


def test_all_six_reference_fixtures_configured():
    assert len(FIXTURES) == 6


def test_critical_mount_platform_and_wargear_covered():
    assert CRITICAL_EFFECTS["OPT0777"] == ("mount", "MOUNT_WAR_BOAR")
    assert CRITICAL_EFFECTS["OPT0719"][0] == "platform"
    assert CRITICAL_EFFECTS["OPT0783"] == ("wargear", "WG_CROSSBOW")


def test_option_expected_quantity_from_json():
    from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS
    ext = "[the-battle-of-five-armies] iron-hills-warrior"
    assert ext in EXTERNAL_PROFILE_IDS
    payload = {"warbands":[{"hero":{"model_id":ext,"options":[]},
       "units":[{"model_id":ext,"quantity":6,
                 "options":[{"id":"OPT0783"}]}]}]}
    assert expected_option_counts(payload)[("IH_WR","OPT0783")] == 6


def test_missing_fixture_is_blocker(tmp_path):
    row=evaluate_one("absent","absent.json",root=tmp_path)
    assert row["status"] == "blocked"
    assert row["issues"] == ["missing_fixture"]


@pytest.fixture(scope="module")
def report():
    return audit()


def test_audit_reports_six_armies(report):
    assert len(report["results"]) == 6


def test_audit_never_approves_scoring(report):
    assert report["calibration_anchors_approved"] is False
    assert report["production_scoring_modified"] is False
    assert report["full_special_rules_approved"] is False


def test_reports_exact_expected_option_for_dain(report):
    five = next(r for r in report["results"] if r["army"] == "five_armies")
    assert any(x["external_option"] == "OPT0777" and
               x["expected_models"] == 1 for x in five["option_checks"])


def test_reports_exact_expected_crossbows(report):
    five = next(r for r in report["results"] if r["army"] == "five_armies")
    assert any(x["external_option"] == "OPT0783" and
               x["expected_models"] == 6 for x in five["option_checks"])


def test_reports_chariot_check(report):
    iron = next(r for r in report["results"] if r["army"] == "iron_hills")
    assert any(x["external_option"] == "OPT0719" for x in iron["option_checks"])


def test_chariot_platform_is_actually_loaded(report):
    iron = next(r for r in report["results"] if r["army"] == "iron_hills")
    row = next(x for x in iron["option_checks"] if x["external_option"] == "OPT0719")
    assert row["effect_confirmed_models"] == 1
    assert iron["status"] == "option_audit_passed"
