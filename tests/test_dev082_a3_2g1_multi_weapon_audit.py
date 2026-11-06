"""DEV-082-A3-2G-1 read-only weapon audit acceptance."""
from copy import deepcopy
import pytest

from offence_multi_weapon_audit import (
    STATES, audit_multi_weapon_report, build_multi_weapon_cohort,
)


def sample():
    return {
        "stage": "DEV-082-A3-2D", "fielded_models": 5,
        "candidate_raw_density": None, "comparable": False,
        "calibration_changed": False, "production_scoring_changed": False,
        "weapon_model_status_counts": {
            "multiple_options": 3, "single_recognised_option": 2,
        },
        "profile_rows": [
            {"profile_id": "MULTI", "quantity": 3,
             "weapon_options": {"status": "multiple_options",
                "candidate_weapon_ids": ["WG_HAND_WEAPON", "WG_TWO_HANDED_WEAPON"],
                "explicit_option_outcomes": [
                    {"weapon_id": "WG_HAND_WEAPON",
                     "uncharged_probability": .4, "charged_probability": .4,
                     "eligible_cavalry_charge_probability": .4},
                    {"weapon_id": "WG_TWO_HANDED_WEAPON",
                     "uncharged_probability": .5, "charged_probability": .6,
                     "eligible_cavalry_charge_probability": .6},
                ]}},
            {"profile_id": "SINGLE", "quantity": 2,
             "weapon_options": {"status": "single_recognised_option",
                "candidate_weapon_ids": ["WG_FANGS"],
                "explicit_option_outcomes": []}},
        ],
    }


def audit(report=None):
    return audit_multi_weapon_report(report or sample(), key="pits_of_dol_guldur")


def test_model_and_profile_counts():
    r = audit()
    assert r["models"] == 5
    assert r["multiple_weapon_models"] == 3
    assert r["multiple_weapon_profiles"] == 1


def test_candidates_and_outcomes_preserved():
    r = audit()
    assert len(r["profile_audits"][0]["alternatives"]) == 2
    assert r["profile_audits"][0]["candidate_weapon_ids"] == [
        "WG_HAND_WEAPON", "WG_TWO_HANDED_WEAPON",
    ]


def test_produces_differences_per_state():
    delta = audit()["profile_audits"][0]["outcome_comparison"]
    assert delta["uncharged_probability"]["spread"] == pytest.approx(.1)
    assert delta["charged_probability"]["spread"] == pytest.approx(.2)


def test_no_choice_or_legality_inferred():
    r = audit()
    assert r["automatic_selection_made"] is False
    assert r["legality_verified"] is False
    assert all(o["battlefield_legality"] == "not_verified"
               for o in r["profile_audits"][0]["alternatives"])


def test_scoring_and_calibration_unchanged():
    r = audit()
    assert r["candidate_raw_density"] is None
    assert r["comparable"] is False
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False


@pytest.mark.parametrize("field,value", [
    ("stage", "DEV-082-A3-2E"),
    ("candidate_raw_density", .8),
    ("comparable", True),
    ("calibration_changed", True),
    ("production_scoring_changed", True),
])
def test_invalid_contract_rejected(field, value):
    data = sample()
    data[field] = value
    with pytest.raises(ValueError):
        audit(data)


def test_rejects_missing_conditional_option():
    d = sample()
    d["profile_rows"][0]["weapon_options"]["explicit_option_outcomes"].pop()
    with pytest.raises(ValueError):
        audit(d)


def test_rejects_duplicate_weapon_candidates():
    d = sample()
    d["profile_rows"][0]["weapon_options"]["candidate_weapon_ids"] = ["WG_HAND_WEAPON"]*2
    with pytest.raises(ValueError):
        audit(d)


@pytest.mark.parametrize("bad", [-.1, 1.1, float("nan")])
def test_rejects_invalid_probability(bad):
    d = sample()
    d["profile_rows"][0]["weapon_options"]["explicit_option_outcomes"][0]["uncharged_probability"] = bad
    with pytest.raises(ValueError):
        audit(d)


def test_rejects_mismatched_counts():
    d = sample()
    d["fielded_models"] = 6
    with pytest.raises(ValueError):
        audit(d)


def test_rejects_mismatched_multi_status_count():
    d = sample()
    d["weapon_model_status_counts"]["multiple_options"] = 2
    with pytest.raises(ValueError):
        audit(d)


def test_does_not_mutate_input():
    d = sample()
    before = deepcopy(d)
    audit(d)
    assert d == before


def test_complete_cohort():
    r = build_multi_weapon_cohort(
        fixtures=[("one", "f1"), ("two", "f2")],
        loader=lambda x: x, weapon_reporter=lambda _: sample(),
    )
    assert r["status"] == "complete"
    assert r["multi_weapon_models"] == 6


def test_partial_cohort_visible():
    def load(path):
        if path == "f2":
            raise ValueError("not importable")
        return path
    r = build_multi_weapon_cohort(
        fixtures=[("one", "f1"), ("two", "f2")],
        loader=load, weapon_reporter=lambda _: sample(),
    )
    assert r["status"] == "incomplete"
    assert r["armies_audited"] == 1
    assert r["rows"][1]["status"] == "blocked"


def test_state_keys_stable():
    assert STATES == (
        "uncharged_probability", "charged_probability",
        "eligible_cavalry_charge_probability",
    )
