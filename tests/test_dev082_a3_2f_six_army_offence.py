"""DEV-082-A3-2F — six-army validation acceptance tests."""
from copy import deepcopy
from pathlib import Path
import pytest
from offence_six_army_validation import (
    COHORT_FIXTURES,
    summarise_army_offence_report,
    build_six_army_offence_cohort,
)


def report():
    state = {"state": "uncharged", "untrapped_probability": 0.4,
             "trapped_probability": 0.6, "absolute_improvement": 0.2}
    return {
        "stage": "DEV-082-A3-2E", "army_points": 700, "fielded_models": 3,
        "legacy_raw_density": 0.693, "candidate_raw_density": None,
        "comparable": False, "production_scoring_changed": False,
        "calibration_changed": False, "trapping_frequency_assumed": False,
        "trapping_benchmark_model_status_counts": {
            "paired_conditional_outcomes": 2,
            "weapon_unresolved_no_trapping_comparison": 1,
        },
        "profile_rows": [
            {
                "profile_id": "ONE", "quantity": 2,
                "weapon_options": {"status": "single_recognised_option"},
                "trapping_benchmark_status": "paired_conditional_outcomes",
                "trapping_benchmark": {
                    "trapping_frequency": None, "trapping_frequency_inferred": False,
                    "conditional_combat_states": [
                        dict(state), {**state, "state": "charged"},
                        {**state, "state": "eligible_cavalry_charge"},
                    ],
                },
                "qualification": {"trapping": {"status": "unresolved"}},
            },
            {
                "profile_id": "TWO", "quantity": 1,
                "weapon_options": {"status": "multiple_recognised_options"},
                "trapping_benchmark_status": "weapon_unresolved_no_trapping_comparison",
                "trapping_benchmark": None,
                "qualification": {"weapon_selection": {"status": "unresolved"}},
            },
        ],
    }


def test_cohort_has_exactly_six_known_fixtures():
    assert len(COHORT_FIXTURES) == 6
    assert len({key for key, _ in COHORT_FIXTURES}) == 6
    assert len({name for _, name in COHORT_FIXTURES}) == 6


def test_summary_quantities_and_coverage():
    r = summarise_army_offence_report("dol_guldur", report())
    assert (r["models"], r["conditional_trapping_models"],
            r["trapping_unresolved_models"]) == (3, 2, 1)


def test_summary_preserves_raw_density_without_candidate():
    r = summarise_army_offence_report("dol_guldur", report())
    assert r["legacy_raw_density"] == pytest.approx(0.693)
    assert r["candidate_raw_density"] is None
    assert r["comparable"] is False


def test_summary_counts_unresolved_by_model():
    r = summarise_army_offence_report("dol_guldur", report())
    assert r["unresolved_condition_model_counts"] == {
        "trapping": 2, "weapon_selection": 1
    }


def test_summary_counts_conditional_effect_by_model_and_state():
    r = summarise_army_offence_report("dol_guldur", report())
    assert r["trapping_effect_model_counts_by_state"] == {
        "charged": 2, "eligible_cavalry_charge": 2, "uncharged": 2
    }


@pytest.mark.parametrize("field,value", [
    ("candidate_raw_density", 0.8), ("comparable", True),
    ("calibration_changed", True), ("production_scoring_changed", True),
    ("trapping_frequency_assumed", True)
])
def test_scoring_or_context_inference_rejected(field, value):
    data = report()
    data[field] = value
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_wrong_stage_rejected():
    data = report()
    data["stage"] = "DEV-082-A3-2D"
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_quantity_mismatch_rejected():
    data = report()
    data["fielded_models"] = 4
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_trap_status_mismatch_rejected():
    data = report()
    data["trapping_benchmark_model_status_counts"] = {}
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_trapping_frequency_must_be_null():
    data = report()
    data["profile_rows"][0]["trapping_benchmark"]["trapping_frequency"] = 0.5
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_trapping_probability_change_must_match_delta():
    data = report()
    data["profile_rows"][0]["trapping_benchmark"]["conditional_combat_states"][0]["absolute_improvement"] = 0.3
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_invalid_probability_rejected():
    data = report()
    data["profile_rows"][0]["trapping_benchmark"]["conditional_combat_states"][0]["trapped_probability"] = 1.1
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_unresolved_row_must_not_have_trapped_outcome():
    data = report()
    data["profile_rows"][1]["trapping_benchmark"] = {"made_up": True}
    with pytest.raises(ValueError):
        summarise_army_offence_report("army", data)


def test_all_six_fixture_paths_and_results(tmp_path):
    for _, filename in COHORT_FIXTURES:
        (tmp_path / filename).write_text("fixture")
    r = build_six_army_offence_cohort(
        fixture_dir=tmp_path, loader=lambda p: p,
        reporter=lambda army: report(),
    )
    assert r["validation_status"] == "six_armies_validated"
    assert r["armies_validated"] == 6
    assert len(r["rows"]) == 6
    assert all(x["status"] == "validated" for x in r["rows"])
    assert r["candidate_raw_density"] is None


def test_missing_army_remains_blocked_and_is_not_hidden(tmp_path):
    _, filename = COHORT_FIXTURES[0]
    (tmp_path / filename).write_text("fixture")
    r = build_six_army_offence_cohort(
        fixture_dir=tmp_path, loader=lambda p: p,
        reporter=lambda army: report(),
    )
    assert r["validation_status"] == "incomplete"
    assert r["armies_validated"] == 1
    assert sum(row["status"] == "blocked" for row in r["rows"]) == 5


def test_failed_import_does_not_abort_other_armies(tmp_path):
    for _, filename in COHORT_FIXTURES:
        (tmp_path / filename).write_text("fixture")
    def loader(p):
        if p.name == COHORT_FIXTURES[0][1]:
            raise ValueError("unimportable")
        return p
    r = build_six_army_offence_cohort(
        fixture_dir=tmp_path, loader=loader,
        reporter=lambda army: report(),
    )
    assert r["armies_validated"] == 5
    assert "unimportable" in r["rows"][0]["reason"]


def test_summary_does_not_mutate_input():
    data = report()
    original = deepcopy(data)
    summarise_army_offence_report("army", data)
    assert data == original
