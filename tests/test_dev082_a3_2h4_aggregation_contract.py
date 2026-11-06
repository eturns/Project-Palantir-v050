"""DEV-082-A3-2H-4 — explicit conditional allocation safeguards."""
from copy import deepcopy
from types import SimpleNamespace as S
import math
import pytest

from offence_explicit_army_aggregation import (
    make_fielded_offence_roster, aggregate_explicit_offence_combats,
    audit_six_army_roster_coverage,
)


def army():
    rows = [
        S(counts_as_model=True, quantity=2,
          configured_profile=S(profile=S(id="INF"), effective_wargear=[
              S(id="WG_HAND_WEAPON"),
          ])),
        S(counts_as_model=True, quantity=2,
          configured_profile=S(profile=S(id="SPEAR"), effective_wargear=[
              S(id="WG_HAND_WEAPON"), S(id="WG_SPEAR"),
          ])),
        S(counts_as_model=False, quantity=1, configured_profile=None),
    ]
    return S(entries=rows, model_count=lambda: 4)


def roster():
    return make_fielded_offence_roster(army())


def joint(f="entry-0001:model-0001", s="entry-0002:model-0001", p=0.36779835390946497):
    return {
        "stage": "DEV-082-A3-2H-3", "status": "conditional_joint_duel_and_wounds",
        "fighter_id": f, "supporter_id": s,
        "support_details": {"support_eligibility": "verified_for_explicit_hypothetical_context"},
        "model_allocation": {"fighters": [f], "supporters": [s],
                             "independent_model_scores_added": False},
        "supporter_not_independent_combat": True,
        "strike_distribution": {"supporter_eligible_strikes": 1},
        "combat_assumptions": {"opponent_wounds": 1, "defender_trapped": False,
                               "attacker_charged": False},
        "combined_kill_probability": p,
        "candidate_raw_density": None,
        "production_scoring_changed": False, "calibration_changed": False,
    }


def independent(f="entry-0001:model-0002", p=0.25):
    return {
        "stage": "DEV-082-A3-2H-4-INDEPENDENT-EVIDENCE",
        "status": "explicit_independent_single_wound_benchmark",
        "fighter_id": f, "opponent_wounds": 1,
        "conditional_context": "explicit_uncharged_untrapped",
        "kill_probability": p,
        "candidate_raw_density": None, "production_scoring_changed": False,
        "calibration_changed": False,
    }


def combined(f="entry-0001:model-0001", s="entry-0002:model-0001", e=None):
    return {"combat_id": "C1", "fighter_ids": [f], "supporter_ids": [s],
            "evidence": e if e is not None else joint(f, s)}


def solo(f="entry-0001:model-0002", e=None, cid="C2"):
    return {"combat_id": cid, "fighter_ids": [f], "supporter_ids": [],
            "evidence": e if e is not None else independent(f)}


def test_unique_model_instance_ids():
    r = roster()
    assert r["model_count"] == 4
    assert len({m["model_id"] for m in r["models"]}) == 4


def test_support_equipment_count_without_role_inference():
    r = roster()
    assert r["potential_support_equipped_count"] == 2
    assert all(m["role"] == "unallocated" for m in r["models"])


def test_siege_entry_not_fielded():
    assert len(roster()["models"]) == 4


def test_empty_allocation_has_no_candidate_or_expected_defeats():
    r = aggregate_explicit_offence_combats(roster(), [])
    assert r["conditional_expected_defeats_across_supplied_opportunities"] is None
    assert r["candidate_raw_density"] is None
    assert r["unallocated_models"] == 4


def test_explicit_joint_combat_mathematically_aggregated():
    r = aggregate_explicit_offence_combats(roster(), [combined()])
    assert r["conditional_expected_defeats_across_supplied_opportunities"] == pytest.approx(.36779835390946497)
    assert r["supported_combats"] == 1
    assert r["allocated_models"] == 2
    assert r["unallocated_models"] == 2


def test_explicit_joint_and_independent_sum():
    r = aggregate_explicit_offence_combats(roster(), [combined(), solo()])
    assert r["conditional_expected_defeats_across_supplied_opportunities"] == pytest.approx(
        .36779835390946497 + .25)
    assert r["allocated_models"] == 3
    assert r["independent_fighters"] == 1


def test_multiple_models_cannot_join_multiple_combats():
    with pytest.raises(ValueError, match="reused"):
        aggregate_explicit_offence_combats(roster(), [
            combined(), solo(f="entry-0001:model-0001",
                             e=independent(f="entry-0001:model-0001")),
        ])


def test_cannot_mark_same_model_fighter_and_supporter():
    with pytest.raises(ValueError, match="both"):
        aggregate_explicit_offence_combats(roster(), [
            combined(s="entry-0001:model-0001")
        ])


def test_supporter_must_have_verified_equipment():
    with pytest.raises(ValueError, match="standard spear"):
        aggregate_explicit_offence_combats(roster(), [
            combined(s="entry-0001:model-0002")
        ])


def test_wrong_supporter_identity_in_evidence():
    with pytest.raises(ValueError, match="IDs"):
        aggregate_explicit_offence_combats(roster(), [
            combined(s="entry-0002:model-0002", e=joint())
        ])


def test_joint_outcome_cannot_be_duel_only():
    d = joint()
    d["status"] = "conditional_duel_calculated"
    with pytest.raises(ValueError, match="Duel AND wounds"):
        aggregate_explicit_offence_combats(roster(), [combined(e=d)])


def test_joint_outcome_cannot_fake_support_legality():
    d = joint()
    d["support_details"] = {}
    with pytest.raises(ValueError, match="eligibility"):
        aggregate_explicit_offence_combats(roster(), [combined(e=d)])


def test_joint_strikes_cannot_be_unverified():
    d = joint()
    d["strike_distribution"]["supporter_eligible_strikes"] = 0
    with pytest.raises(ValueError, match="Strike"):
        aggregate_explicit_offence_combats(roster(), [combined(e=d)])


def test_joint_target_must_be_single_wound():
    d = joint()
    d["combat_assumptions"]["opponent_wounds"] = 2
    with pytest.raises(ValueError, match="one-wound"):
        aggregate_explicit_offence_combats(roster(), [combined(e=d)])


@pytest.mark.parametrize("prob", [-0.1, 1.1, float("nan"), float("inf"), None])
def test_nonprobability_rejected(prob):
    with pytest.raises(ValueError, match="probability"):
        aggregate_explicit_offence_combats(roster(), [combined(e=joint(p=prob))])


def test_uncalibrated_conditional_sum_never_replaces_density():
    r = aggregate_explicit_offence_combats(roster(), [combined(), solo()])
    assert r["candidate_raw_density"] is None
    assert r["comparable_with_legacy_army_density"] is False
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False
    assert r["scenario_score"] is None


def test_no_inferred_opportunities_from_empty_roster():
    r = aggregate_explicit_offence_combats(roster(), [])
    assert r["combat_opportunity_frequency_inferred"] is False
    assert r["deployment_frequency_inferred"] is False


def test_duplicate_combat_id_rejected():
    with pytest.raises(ValueError, match="Combat IDs"):
        aggregate_explicit_offence_combats(roster(), [combined(), combined()])


def test_nonexistent_model_rejected():
    with pytest.raises(ValueError, match="non-roster"):
        aggregate_explicit_offence_combats(roster(), [
            solo(f="bogus", e=independent(f="bogus"))
        ])


def test_support_only_combat_rejected():
    bad = {"combat_id": "C9", "fighter_ids": [],
           "supporter_ids": ["entry-0002:model-0001"], "evidence": joint()}
    with pytest.raises(ValueError, match="frontline"):
        aggregate_explicit_offence_combats(roster(), [bad])


def test_independent_evidence_must_bind_identity():
    with pytest.raises(ValueError, match="fighter ID"):
        aggregate_explicit_offence_combats(roster(), [
            solo(e=independent(f="entry-0001:model-0001"))
        ])


def test_independent_requires_explicit_context():
    bad = independent()
    bad["conditional_context"] = "unspecified"
    with pytest.raises(ValueError, match="context"):
        aggregate_explicit_offence_combats(roster(), [solo(e=bad)])


def test_does_not_mutate_roster_or_evidence():
    rs = roster()
    cb = [combined(), solo()]
    before_rs, before_cb = deepcopy(rs), deepcopy(cb)
    aggregate_explicit_offence_combats(rs, cb)
    assert rs == before_rs
    assert cb == before_cb


def test_roster_count_mismatch_rejected():
    rs = roster()
    rs["model_count"] = 7
    with pytest.raises(ValueError, match="count"):
        aggregate_explicit_offence_combats(rs, [])


def test_all_six_army_census_with_mock_loader():
    r = audit_six_army_roster_coverage(
        fixtures=[(f"army{i}", f"fixture{i}") for i in range(6)],
        loader=lambda _: army(),
    )
    assert r["status"] == "six_armies_audited"
    assert r["armies_audited"] == 6
    assert r["models_examined"] == 24
    assert r["potential_support_equipped_models"] == 12
    assert r["combat_allocations_inferred"] == 0


def test_census_keeps_failed_army_visible():
    def loader(name):
        if name == "broken": raise ValueError("missing")
        return army()
    r = audit_six_army_roster_coverage(
        fixtures=[("good", "good"), ("bad", "broken")], loader=loader,
    )
    assert r["status"] == "incomplete"
    assert r["rows"][1]["status"] == "blocked"


def test_empty_army_supported_as_empty_roster():
    empty = S(entries=[], model_count=lambda: 0)
    r = make_fielded_offence_roster(empty)
    assert r["model_count"] == 0


def test_model_reconciliation_rejects_stale_count():
    fake = army()
    fake.model_count = lambda: 5
    with pytest.raises(ValueError, match="reconcile"):
        make_fielded_offence_roster(fake)
