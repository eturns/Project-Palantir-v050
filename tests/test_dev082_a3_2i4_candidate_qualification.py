"""DEV-082-A3-2I-4 arithmetic, identity, nonpromotion acceptance."""
from copy import deepcopy
import pytest
from offence_candidate_metric_qualification import (
    qualify_neutral_metric_army, audit_neutral_metric_cohort,
)


def sources(key="example", unresolved=False):
    rows = [
        dict(entry_index=1, profile_id="A", quantity=2,
             qualification="single_option_neutral_reference",
             neutral_single_model_probability=.25,
             selected_weapon_id=None, support_placement_inferred=False,
             weapon_option_evidence=None),
        dict(entry_index=2, profile_id="B", quantity=3,
             qualification="benchmark_equivalent_neutral_reference",
             neutral_single_model_probability=.5,
             selected_weapon_id=None, support_placement_inferred=False,
             weapon_option_evidence=dict(
                 all_comparison_states_equivalent=True,
                 weapon_legality="not_verified",
                 uncharged_probability_range=[.5,.5])),
    ]
    if unresolved:
        rows.append(dict(
            entry_index=3, profile_id="C", quantity=2,
            qualification="different_weapon_outcomes_unresolved",
            neutral_single_model_probability=None,
            selected_weapon_id=None, support_placement_inferred=False,
            weapon_option_evidence=dict(
                all_comparison_states_equivalent=False,
                weapon_legality="not_verified",
                uncharged_probability_range=[.2,.4])))
    models=7 if unresolved else 5
    covers=dict(key=key, status="neutral_coverage_qualified",
                models=models, points=100., neutral_reference_models=5,
                different_weapon_outcome_models=2 if unresolved else 0,
                new_benchmark_equivalent_models=3,
                profile_evidence=rows,
                candidate_raw_density=None,
                production_scoring_changed=False,
                calibration_changed=False,
                comparable_with_legacy_army_density=False,
                support_deployment_inferred=False,
                conditional_frequencies_inferred=False)
    entries=[]
    for row in rows:
        value=row["neutral_single_model_probability"]
        if value is None:
            bounds=[.2,.4]
        else:
            bounds=[value,value]
        entries.append(dict(entry_index=row["entry_index"],
                            profile_id=row["profile_id"],
                            quantity=row["quantity"],
                            qualification=row["qualification"],
                            neutral_probability_per_model=value,
                            conditional_range_per_model=bounds,
                            selected_weapon_id=None))
    low=2.0 + (.4 if unresolved else 0)
    high=2.0 + (.8 if unresolved else 0)
    numerical=dict(
        key=key,status="complete_conditional_reference",points=100.,
        models=models,
        per_entry_evidence=entries,
        neutral_reference_models=5,
        weapon_alternative_models=2 if unresolved else 0,
        unquantified_models=0,
        fixed_qualified_expected_defeats=2.0,
        conditional_total_expected_defeats_lower=low,
        conditional_total_expected_defeats_upper=high,
        neutral_direct_melee_density_lower_per_100pts=low,
        neutral_direct_melee_density_upper_per_100pts=high,
        neutral_direct_melee_density_point_per_100pts=(
            None if unresolved else 2.0),
        normalisation_unit="conditional_expected_single_wound_defeats_per_100_army_points",
        comparison_scope="uncharged_untrapped_independent_models_fixed_benchmark",
        weapon_interval_scope="unverified_alternative_scenario_envelope_not_optimal_selection",
        unresolved_options_selected=False,
        deployment_frequency_inferred=False,
        support_combat_benefit_included=False,
        charged_or_trapping_benefit_included=False,
        comparable_with_legacy_production_density=False,
        candidate_raw_density=None,
        production_scoring_changed=False,
        calibration_changed=False)
    methodology=dict(
        key=key,status="methodology_qualified",points=100.,models=models,
        legacy_raw_density_production_reference_only=2.0,
        candidate_raw_density=None,
        production_scoring_changed=False,
        calibration_changed=False,
        legacy_and_neutral_scores_comparable=False,
        conditional_weights=None)
    return numerical,covers,methodology


def qualify(unresolved=False):
    return qualify_neutral_metric_army(*sources(unresolved=unresolved))


def test_independent_per_entry_reconciliation():
    r=qualify()
    assert sum(x["conditional_expected_defeats_lower"]
               for x in r["entry_contributions"]) == pytest.approx(2.)
    assert r["per_entry_contribution_count"] == 2


def test_units_and_density_per_100_points():
    r=qualify()
    assert r["neutral_density_point_per_100pts"] == pytest.approx(2.)


def test_alternative_range_preserved():
    r=qualify(True)
    assert r["neutral_density_lower_per_100pts"] == pytest.approx(2.4)
    assert r["neutral_density_upper_per_100pts"] == pytest.approx(2.8)
    assert r["neutral_density_point_per_100pts"] is None


def test_numerical_legacy_match_does_not_imply_equivalence():
    r=qualify()
    assert r["legacy_neutral_numerically_equal"] is True
    assert r["comparable_with_legacy_production_density"] is False
    assert "not_yet_verified" in r["legacy_match_interpretation"]


def test_numerical_nonmatch_produces_no_delta():
    n,c,m=sources()
    m["legacy_raw_density_production_reference_only"]=1.3
    r=qualify_neutral_metric_army(n,c,m)
    assert r["legacy_neutral_numerically_equal"] is False
    assert r["candidate_raw_density"] is None


def test_frozen_contract_prohibits_promoting_score():
    r=qualify()
    assert r["candidate_qualification"] == "diagnostic_only_not_production_approved"
    assert r["promote_to_dashboard"] is False
    assert r["candidate_raw_density"] is None
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False


def test_sources_immutable():
    source=sources(True)
    before=deepcopy(source)
    qualify_neutral_metric_army(*source)
    assert source==before


@pytest.mark.parametrize("field,value",[
    ("candidate_raw_density",.5),
    ("production_scoring_changed",True),
    ("calibration_changed",True),
    ("comparable_with_legacy_production_density",True),
    ("unresolved_options_selected",True),
    ("deployment_frequency_inferred",True),
    ("support_combat_benefit_included",True),
    ("charged_or_trapping_benefit_included",True),
])
def test_production_or_context_contract_rejected(field,value):
    n,c,m=sources()
    n[field]=value
    with pytest.raises(ValueError):
        qualify_neutral_metric_army(n,c,m)


@pytest.mark.parametrize("field,value",[
    ("fixed_qualified_expected_defeats",2.1),
    ("conditional_total_expected_defeats_lower",2.1),
    ("conditional_total_expected_defeats_upper",2.1),
    ("neutral_direct_melee_density_lower_per_100pts",2.1),
    ("neutral_direct_melee_density_point_per_100pts",2.1),
])
def test_incorrect_aggregate_rejected(field,value):
    n,c,m=sources()
    n[field]=value
    with pytest.raises(ValueError, match="reconcile"):
        qualify_neutral_metric_army(n,c,m)


def test_duplicated_entry_rejected():
    n,c,m=sources()
    c["profile_evidence"][1]["entry_index"]=1
    with pytest.raises(ValueError,match="Duplicate"):
        qualify_neutral_metric_army(n,c,m)


def test_entry_identity_cross_stage_mismatch_rejected():
    n,c,m=sources()
    n["per_entry_evidence"][1]["profile_id"]="INCORRECT"
    with pytest.raises(ValueError,match="does not match"):
        qualify_neutral_metric_army(n,c,m)


def test_unresolved_cannot_have_point():
    n,c,m=sources(unresolved=True)
    n["neutral_direct_melee_density_point_per_100pts"]=2.6
    with pytest.raises(ValueError,match="Interval"):
        qualify_neutral_metric_army(n,c,m)


def test_weapon_legality_cannot_be_silently_asserted():
    n,c,m=sources()
    c["profile_evidence"][1]["weapon_option_evidence"]["weapon_legality"]="verified"
    with pytest.raises(ValueError):
        qualify_neutral_metric_army(n,c,m)


def test_bad_army_points_rejected():
    n,c,m=sources()
    n["points"]=0
    with pytest.raises(ValueError):
        qualify_neutral_metric_army(n,c,m)


def test_different_army_keys_rejected():
    n,c,m=sources()
    c["key"]="another"
    with pytest.raises(ValueError,match="identity"):
        qualify_neutral_metric_army(n,c,m)


def cohort():
    arrays=[sources(key=f"army{i}",unresolved=(i==2)) for i in range(6)]
    n=dict(stage="DEV-082-A3-2I-3",status="six_armies_compared",
           rows=[x[0] for x in arrays],
           models_examined=sum(x[0]["models"] for x in arrays),
           candidate_raw_density=None,
           production_scoring_changed=False,calibration_changed=False)
    c=dict(stage="DEV-082-A3-2I-2",status="six_armies_qualified",
           rows=[x[1] for x in arrays],candidate_raw_density=None,
           production_scoring_changed=False,calibration_changed=False)
    m=dict(stage="DEV-082-A3-2I-1",status="six_armies_qualified",
           rows=[x[2] for x in arrays],candidate_raw_density=None,
           production_scoring_changed=False,calibration_changed=False)
    return n,c,m


def test_six_army_cohort_qualified():
    r=audit_neutral_metric_cohort(*cohort())
    assert r["status"]=="six_armies_arithmetic_audited"
    assert r["armies_audited"]==6
    assert r["models_examined"]==32
    assert r["weapon_alternative_models"]==2
    assert r["promotion_decision"].startswith("blocked")


def test_six_army_order_mismatch_fails():
    n,c,m=cohort()
    c["rows"].reverse()
    with pytest.raises(ValueError,match="same unique order"):
        audit_neutral_metric_cohort(n,c,m)


def test_missing_reference_army_fails():
    n,c,m=cohort()
    m["rows"].pop()
    with pytest.raises(ValueError,match="Six rows"):
        audit_neutral_metric_cohort(n,c,m)


def test_mismatch_cohort_total_fails():
    n,c,m=cohort()
    n["models_examined"]+=1
    with pytest.raises(ValueError,match="totals"):
        audit_neutral_metric_cohort(n,c,m)


def test_same_rank_not_emitted():
    r=audit_neutral_metric_cohort(*cohort())
    assert r["rankings_generated"] is False


@pytest.mark.parametrize("field, bad",[
    ("comparison_scope","some-other-benchmark"),
    ("normalisation_unit","unitless"),
    ("weapon_interval_scope","best-case-optimal"),
])
def test_scope_tampering_rejected(field,bad):
    n,c,m=sources()
    n[field]=bad
    with pytest.raises(ValueError,match="provenance"):
        qualify_neutral_metric_army(n,c,m)
