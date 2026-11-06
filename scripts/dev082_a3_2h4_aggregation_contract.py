"""DEV-082-A3-2H-4 — six-army roster census + one hypothetical combat.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
Read only. Never infers battlefield position, matching or opportunities.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_six_army_validation import COHORT_FIXTURES
from offence_explicit_support_combat import ExplicitSupportContext
from offence_joint_support_wounds import calculate_explicit_joint_support_kill
from offence_explicit_army_aggregation import (
    make_fielded_offence_roster,
    audit_six_army_roster_coverage,
    aggregate_explicit_offence_combats,
)


def load_army(path):
    result = run_analysis_workflow(str(path), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Real imported army unavailable")
    return result["army"]


def example_iron_hills(fixture_dir):
    army = load_army(fixture_dir / "iron-hills-cal.json")
    roster = make_fielded_offence_roster(army)
    front = support = None
    for idx, entry in enumerate(army.entries, start=1):
        if not entry.counts_as_model or entry.profile.id != "IH_WR":
            continue
        gear = {x.id for x in entry.configured_profile.effective_wargear}
        model_id = f"entry-{idx:04d}:model-0001"
        if "WG_SPEAR" in gear and support is None:
            support = (model_id, entry.configured_profile)
        elif "WG_SPEAR" not in gear and front is None:
            front = (model_id, entry.configured_profile)
    if not front or not support:
        raise ValueError("Required two Iron Hills Warrior configurations absent")
    evidence = calculate_explicit_joint_support_kill(
        front[1], support[1], fighter_id=front[0], supporter_id=support[0],
        context=ExplicitSupportContext.conditional_example(),
    )
    report = aggregate_explicit_offence_combats(roster, [{
        "combat_id": "hypothetical-iron-hills-support-01",
        "fighter_ids": [front[0]], "supporter_ids": [support[0]],
        "evidence": evidence,
    }])
    report["example_scope"] = (
        "ONE deliberately specified uncharged, untrapped combat; "
        "not a predicted fight or whole-army score"
    )
    return report


def main():
    fixture_dir = ROOT / "tests" / "fixtures"
    report = audit_six_army_roster_coverage(
        fixtures=[(key, fixture_dir / filename)
                  for key, filename in COHORT_FIXTURES],
        loader=load_army,
    )
    try:
        report["hypothetical_iron_hills_example"] = example_iron_hills(fixture_dir)
    except Exception as exc:
        report["hypothetical_iron_hills_example"] = {
            "status": "blocked", "reason": f"{type(exc).__name__}: {exc}"
        }
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
