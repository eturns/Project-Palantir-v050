"""Project Palantír — DEV-082-A3-2H-4 explicit combat aggregation contract.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Read-only. Construct a deterministic fielded model roster and sum ONLY
explicitly supplied, validated combat-level probabilities. Models may be
allocated at most once. No automatic opponent selection, frontline/support
deployment, combat frequency, availability or army-wide Offence score.

A sum of conditional combat probabilities is NOT an army forecast: it
assumes each listed combat is an independent *specified opportunity* and
reports an expected number of defeated single-wound benchmarks across
those *specified* opportunities only.
"""
from __future__ import annotations

from math import isfinite


SUPPORT_IDS = frozenset({"WG_SPEAR", "WG_WAR_SPEAR"})


def make_fielded_offence_roster(army) -> dict:
    """Expand real Army entries into unique records. No battlefield roles."""
    records = []
    for entry_idx, entry in enumerate(army.entries, start=1):
        if not entry.counts_as_model:
            continue
        if entry.configured_profile is None:
            raise ValueError("Model entry missing ConfiguredProfile")
        quantity = entry.quantity
        if type(quantity) is not int or quantity <= 0:
            raise ValueError("Invalid model quantity")
        configured = entry.configured_profile
        wargear = sorted({w.id for w in configured.effective_wargear})
        for instance in range(1, quantity + 1):
            records.append({
                "model_id": f"entry-{entry_idx:04d}:model-{instance:04d}",
                "entry_index": entry_idx,
                "instance_index": instance,
                "profile_id": configured.profile.id,
                "support_wargear_ids": sorted(set(wargear) & SUPPORT_IDS),
                "role": "unallocated",
            })
    if len(records) != army.model_count():
        raise ValueError("Roster does not reconcile with Army.model_count")
    if len(records) != len({m["model_id"] for m in records}):
        raise ValueError("Duplicate roster model IDs")
    return {
        "models": records,
        "model_count": len(records),
        "potential_support_equipped_count": sum(
            bool(m["support_wargear_ids"]) for m in records
        ),
        "allocation_status": "not_inferred",
    }


def _finite_probability(value, name):
    if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} requires a finite probability from 0 to 1")
    return float(value)


def _unique_nonblank(values, label):
    if not isinstance(values, list):
        raise ValueError(f"{label} must be a list")
    if any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError(f"{label} requires nonblank model IDs")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} has duplicate model IDs")


def _verify_combat_evidence(combat, fighters, supporters):
    """Accept only evidence tied to the exact stated model identities."""
    evidence = combat.get("evidence")
    if not isinstance(evidence, dict):
        raise ValueError("Combat requires explicit evidence")
    if evidence.get("production_scoring_changed") is not False:
        raise ValueError("Production scoring must remain unchanged")
    if evidence.get("calibration_changed") is not False:
        raise ValueError("Calibration must remain unchanged")
    if evidence.get("candidate_raw_density") is not None:
        raise ValueError("Candidate production density is not permitted")
    if supporters:
        # H3 is precisely one fighter and one verified hypothetical supporter.
        if len(fighters) != 1 or len(supporters) != 1:
            raise ValueError("A3-2H-3 only qualifies one fighter + one supporter")
        if evidence.get("stage") != "DEV-082-A3-2H-3":
            raise ValueError("Supporting combat requires validated H3 result")
        if evidence.get("status") != "conditional_joint_duel_and_wounds":
            raise ValueError("Supporting combat must include Duel AND wounds")
        if evidence.get("fighter_id") != fighters[0] or evidence.get("supporter_id") != supporters[0]:
            raise ValueError("Joint combat evidence IDs do not match allocation")
        allocation = evidence.get("model_allocation", {})
        if allocation.get("fighters") != fighters or allocation.get("supporters") != supporters:
            raise ValueError("Evidence allocation disagrees with specified combat")
        if allocation.get("independent_model_scores_added") is not False:
            raise ValueError("Supporting model has independent score")
        if evidence.get("supporter_not_independent_combat") is not True:
            raise ValueError("Supporter incorrectly represented as independent")
        if evidence.get("support_details", {}).get("support_eligibility") != (
            "verified_for_explicit_hypothetical_context"
        ):
            raise ValueError("Explicit support eligibility evidence missing")
        assumptions = evidence.get("combat_assumptions", {})
        if assumptions.get("opponent_wounds") != 1:
            raise ValueError("Joint combat must target one-wound benchmark")
        if assumptions.get("defender_trapped") is not False:
            raise ValueError("Unsupported trapped scenario")
        if assumptions.get("attacker_charged") is not False:
            raise ValueError("Unsupported charge scenario")
        if evidence.get("strike_distribution", {}).get("supporter_eligible_strikes") != 1:
            raise ValueError("Supporting Strike count not verified")
        return _finite_probability(evidence.get("combined_kill_probability"), "joint kill")
    # Independent baseline is only accepted with explicit outcome and identity,
    # not calculated from the presence of an unallocated army model.
    if len(fighters) != 1:
        raise ValueError("Independent conditional combat requires exactly one fighter")
    if evidence.get("stage") != "DEV-082-A3-2H-4-INDEPENDENT-EVIDENCE":
        raise ValueError("Independent outcome must be explicitly qualified")
    if evidence.get("status") != "explicit_independent_single_wound_benchmark":
        raise ValueError("Independent outcome not qualified")
    if evidence.get("fighter_id") != fighters[0]:
        raise ValueError("Independent fighter ID does not match")
    if evidence.get("opponent_wounds") != 1:
        raise ValueError("Only one-wound targets in this contract")
    if evidence.get("conditional_context") != "explicit_uncharged_untrapped":
        raise ValueError("Independent context missing")
    return _finite_probability(evidence.get("kill_probability"), "independent kill")


def aggregate_explicit_offence_combats(roster: dict, combats: list[dict]) -> dict:
    """Validate role conservation and sum eligible specified combat outcomes.

    Does NOT estimate deployment, activation probability, or army-wide density.
    All results remain conditional evidence, not a replacement Offence score.
    """
    if not isinstance(roster, dict) or not isinstance(combats, list):
        raise ValueError("Roster and combat list required")
    models = roster.get("models")
    if not isinstance(models, list):
        raise ValueError("Malformed roster")
    ids = [m.get("model_id") for m in models]
    _unique_nonblank(ids, "roster")
    if roster.get("model_count") != len(ids):
        raise ValueError("Roster count mismatch")
    model_by_id = {m["model_id"]: m for m in models}
    used, seen_combat_ids = set(), set()
    entries = []
    total = 0.0
    for combat in combats:
        cid = combat.get("combat_id")
        if not isinstance(cid, str) or not cid.strip() or cid in seen_combat_ids:
            raise ValueError("Combat IDs must be unique and nonblank")
        seen_combat_ids.add(cid)
        fighters = combat.get("fighter_ids")
        supporters = combat.get("supporter_ids")
        _unique_nonblank(fighters, "fighter_ids")
        _unique_nonblank(supporters, "supporter_ids")
        if not fighters:
            raise ValueError("A combat must contain a frontline fighter")
        combined = fighters + supporters
        if len(combined) != len(set(combined)):
            raise ValueError("A model cannot be both fighter and supporter")
        if not set(combined).issubset(model_by_id):
            raise ValueError("Combat uses non-roster models")
        if used.intersection(combined):
            raise ValueError("Model reused across combat opportunities")
        if supporters:
            for sid in supporters:
                if "WG_SPEAR" not in model_by_id[sid].get("support_wargear_ids", []):
                    raise ValueError("Spear supporter not equipped with verified standard spear")
        probability = _verify_combat_evidence(combat, fighters, supporters)
        used.update(combined)
        total += probability
        entries.append({
            "combat_id": cid, "fighter_ids": list(fighters),
            "supporter_ids": list(supporters),
            "conditional_single_wound_kill_probability": probability,
            "evidence_stage": combat["evidence"]["stage"],
        })
    return {
        "stage": "DEV-082-A3-2H-4",
        "status": "explicit_conditional_allocation_validated",
        "roster_models": len(ids),
        "allocated_models": len(used),
        "unallocated_models": len(ids) - len(used),
        "independent_fighters": sum(not x["supporter_ids"] for x in entries),
        "supported_combats": sum(bool(x["supporter_ids"]) for x in entries),
        "supporters_allocated": sum(len(x["supporter_ids"]) for x in entries),
        "combat_opportunities_explicitly_supplied": len(entries),
        "conditional_expected_defeats_across_supplied_opportunities": (
            total if entries else None
        ),
        "expected_defeats_scope": (
            "sum_of_conditional_individually_specified_single_wound_combat_opportunities"
        ),
        "combat_evidence": entries,
        "deployment_frequency_inferred": False,
        "combat_opportunity_frequency_inferred": False,
        "unallocated_model_combat_contribution": None,
        "candidate_raw_density": None,
        "comparable_with_legacy_army_density": False,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }


def audit_six_army_roster_coverage(*, fixtures, loader) -> dict:
    """Only a roster census. Inferred combat allocations are forbidden."""
    rows = []
    for key, path in fixtures:
        try:
            roster = make_fielded_offence_roster(loader(path))
            empty = aggregate_explicit_offence_combats(roster, [])
            rows.append({
                "key": key, "status": "audited",
                "models": roster["model_count"],
                "support_equipped_models": roster["potential_support_equipped_count"],
                "allocated_models": empty["allocated_models"],
                "conditional_expected_defeats": empty[
                    "conditional_expected_defeats_across_supplied_opportunities"
                ],
            })
        except Exception as exc:
            rows.append({"key": key, "status": "blocked",
                         "reason": f"{type(exc).__name__}: {exc}"})
    audited = [row for row in rows if row["status"] == "audited"]
    return {
        "stage": "DEV-082-A3-2H-4",
        "status": ("six_armies_audited" if len(rows) == 6 and len(audited) == 6
                   else "incomplete"),
        "armies_audited": len(audited),
        "armies_expected": len(rows),
        "models_examined": sum(r["models"] for r in audited),
        "potential_support_equipped_models": sum(
            r["support_equipped_models"] for r in audited
        ),
        "combat_allocations_inferred": 0,
        "rows": rows,
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
