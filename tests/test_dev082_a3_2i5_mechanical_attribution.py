"""Project Palantír DEV-082-A3-2I-5 attribution and nonpromotion tests."""
from copy import deepcopy
from types import SimpleNamespace as NS
import pytest
from offence_mechanical_attribution import (
    replay_legacy_profile_states,
    attribute_army_neutral_difference,
    attribute_six_armies,
)


def fixture_aligned(*, mismatch=False, alternative=False, charge_effect=True):
    row = dict(entry_index=1, profile_id="A", quantity=2,
               qualification="single_option_neutral_reference",
               conditional_expected_defeats_lower=.5 if not mismatch else .6,
               conditional_expected_defeats_upper=.5 if not mismatch else .6)
    replay = [dict(entry_index=1, profile_id="A", quantity=2,
                   legacy_uncharged_per_model=.25,
                   legacy_charged_per_model=.35 if charge_effect else .25,
                   charge_parameter_effect_per_model=.10 if charge_effect else 0.)]
    if alternative:
        row2 = dict(entry_index=2, profile_id="B", quantity=3,
                    qualification="different_weapon_outcomes_unresolved",
                    conditional_expected_defeats_lower=.6,
                    conditional_expected_defeats_upper=.9)
        rowset = [row, row2]
        replay += [dict(entry_index=2, profile_id="B", quantity=3,
                        legacy_uncharged_per_model=.3,
                        legacy_charged_per_model=.3,
                        charge_parameter_effect_per_model=0.)]
    else:
        rowset = [row]
    points=100.
    charged = sum(x["quantity"]*x["legacy_charged_per_model"] for x in replay)
    q=dict(key="sample", status="arithmetic_and_provenance_qualified",
           points=points, models=5 if alternative else 2,
           weapon_alternative_models=3 if alternative else 0,
           entry_contributions=rowset,
           legacy_production_reference_only=charged,
           legacy_neutral_numerically_equal=not charge_effect and not alternative,
           candidate_raw_density=None, promote_to_dashboard=False,
           production_scoring_changed=False, calibration_changed=False,
           comparable_with_legacy_production_density=False)
    return q, replay


def army(models=("A",2,.25,.35)):
    entries=[]
    for profile_id, qty, neutral, charged in [models]:
        entries.append(NS(counts_as_model=True, quantity=qty,
                          configured_profile=NS(profile=NS(id=profile_id), neutral=neutral, charged=charged)))
    entries.append(NS(counts_as_model=False, quantity=1, configured_profile=None))
    return NS(entries=entries, model_count=lambda:sum(e.quantity for e in entries if e.counts_as_model))


def scorer(profile, p):
    return profile.charged if p == 1.0 else profile.neutral


def test_real_entry_replay_passes_both_charge_states():
    result=replay_legacy_profile_states(army(), scorer=scorer)
    assert result[0]["legacy_uncharged_per_model"] == .25
    assert result[0]["legacy_charged_per_model"] == .35


def test_legacy_replay_reconciles_charged_density():
    q,r=fixture_aligned()
    result=attribute_army_neutral_difference(q,r,production_check=.70)
    assert result["legacy_charged_replay_matches_production"] is True
    assert result["legacy_charged_replayed_density"] == pytest.approx(.7)


def test_profile_match_attributing_only_charge_parameter_difference():
    q,r=fixture_aligned()
    result=attribute_army_neutral_difference(q,r)
    assert result["neutral_matched_models"] == 2
    assert result["full_difference_attribution_possible"] is True
    assert result["known_charge_parameter_contributions_per_100pts"] == pytest.approx(.2)
    assert result["profile_rows_evidence"][0]["attribution"] == "charge_parameter_difference_isolated"


def test_exact_match_without_charge_effect_not_causal_proof():
    q,r=fixture_aligned(charge_effect=False)
    result=attribute_army_neutral_difference(q,r)
    assert result["legacy_and_neutral_numerically_equal"] is True
    assert result["profile_rows_evidence"][0]["attribution"] == "same_replay_result_at_both_charge_parameters"
    assert result["promotion_authorised"] is False


def test_profile_mismatch_blocks_full_attribution():
    q,r=fixture_aligned(mismatch=True)
    result=attribute_army_neutral_difference(q,r)
    assert result["full_difference_attribution_possible"] is False
    assert result["neutral_mismatched_models"] == 2
    assert result["unexplained_profile_mismatches"] == 1


def test_weapon_alternative_remains_unknown_and_partial():
    q,r=fixture_aligned(alternative=True)
    result=attribute_army_neutral_difference(q,r)
    assert result["weapon_choice_unresolved_models"] == 3
    assert result["full_difference_attribution_possible"] is False
    assert result["profile_rows_evidence"][1]["replay_uncharged_matches_neutral"] is None


def test_no_production_change_or_score():
    q,r=fixture_aligned()
    result=attribute_army_neutral_difference(q,r)
    assert result["candidate_raw_density"] is None
    assert result["calibration_changed"] is False
    assert result["production_scoring_changed"] is False
    assert result["dashboard_score"] is None
    assert result["metric_decision"].startswith("retain_separate")


def test_input_is_never_mutated():
    q,r=fixture_aligned(alternative=True)
    saved=deepcopy((q,r))
    attribute_army_neutral_difference(q,r)
    assert (q,r)==saved


@pytest.mark.parametrize("path,bad",[
    ("candidate_raw_density",.4),
    ("promote_to_dashboard",True),
    ("production_scoring_changed",True),
    ("calibration_changed",True),
    ("comparable_with_legacy_production_density",True),
])
def test_bad_contract_rejected(path,bad):
    q,r=fixture_aligned()
    q[path]=bad
    with pytest.raises(ValueError,match="contract"):
        attribute_army_neutral_difference(q,r)


@pytest.mark.parametrize("field,bad",[
    ("legacy_production_reference_only",.9),
    ("points",70.),
])
def test_legacy_reconciliation_fails_closed(field,bad):
    q,r=fixture_aligned()
    q[field]=bad
    with pytest.raises(ValueError,match="does not match"):
        attribute_army_neutral_difference(q,r)


def test_explicit_direct_legacy_check_rejected_when_mismatch():
    q,r=fixture_aligned()
    with pytest.raises(ValueError,match="differs from production"):
        attribute_army_neutral_difference(q,r,production_check=.8)


def test_no_duplicate_replay_profiles():
    q,r=fixture_aligned(alternative=True)
    r[1]["entry_index"]=1
    with pytest.raises(ValueError,match="model identity"):
        attribute_army_neutral_difference(q,r)


def test_no_silent_option_resolution():
    q,r=fixture_aligned(alternative=True)
    assert attribute_army_neutral_difference(q,r)["profile_rows_evidence"][1]["attribution"] == "weapon_selection_unresolved_no_causal_attribution"


def test_inconsistent_charge_delta_rejected():
    q,r=fixture_aligned()
    r[0]["charge_parameter_effect_per_model"] = .8
    with pytest.raises(ValueError,match="Inconsistent"):
        attribute_army_neutral_difference(q,r)


def test_model_quantity_mismatch_rejected():
    q,r=fixture_aligned()
    r[0]["quantity"]=3
    with pytest.raises(ValueError,match="model identity"):
        attribute_army_neutral_difference(q,r)


def test_profile_identity_mismatch_rejected():
    q,r=fixture_aligned()
    r[0]["profile_id"]="WRONG"
    with pytest.raises(ValueError,match="model identity"):
        attribute_army_neutral_difference(q,r)


def test_invalid_replay_probability_rejected():
    with pytest.raises(ValueError,match="Invalid"):
        replay_legacy_profile_states(army(),scorer=lambda a,p:float("nan"))


def test_invalid_replay_quantity_rejected():
    a=army()
    a.entries[0].quantity=0
    with pytest.raises(ValueError,match="quantity"):
        replay_legacy_profile_states(a,scorer=scorer)


def test_unfielded_models_ignored():
    r=replay_legacy_profile_states(army(),scorer=scorer)
    assert len(r)==1
    assert r[0]["quantity"]==2


def test_nonprofile_neutral_status_rejected():
    q,r=fixture_aligned()
    q["entry_contributions"][0]["qualification"]="unresolved"
    with pytest.raises(ValueError,match="Unsupported"):
        attribute_army_neutral_difference(q,r)


def test_bad_qualified_neutral_bounds_rejected():
    q,r=fixture_aligned()
    q["entry_contributions"][0]["conditional_expected_defeats_upper"] = .7
    with pytest.raises(ValueError,match="point"):
        attribute_army_neutral_difference(q,r)


def test_6_army_cohort_without_production_mutation():
    sources=[]
    for i in range(6):
        q,_=fixture_aligned()
        q["key"]=f"army{i}"
        sources.append(q)
    cohort=dict(status="six_armies_arithmetic_audited",rows=sources,models_examined=12)
    output=attribute_six_armies(cohort,[army() for _ in range(6)],
                                scorer=scorer,production_calculator=lambda a:.7)
    assert output["status"]=="six_armies_attributed"
    assert output["models_examined"]==12
    assert len(output["full_profile_attribution_armies"])==6
    assert output["promotion_authorised"] is False


def test_mismatched_cohort_model_count_rejected():
    q,r=fixture_aligned()
    cohort=dict(status="six_armies_arithmetic_audited",rows=[dict(q,key=f"army{i}") for i in range(6)],models_examined=13)
    with pytest.raises(ValueError,match="count mismatch"):
        attribute_six_armies(cohort,[army() for _ in range(6)],scorer=scorer)


def test_fewer_than_six_armies_rejected():
    with pytest.raises(ValueError,match="complete"):
        attribute_six_armies(dict(status="six_armies_arithmetic_audited",rows=[]),[],scorer=scorer)
