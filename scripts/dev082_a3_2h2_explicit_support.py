"""DEV-082-A3-2H-2 — conditional Iron Hills spear-support example.

Assumes a hypothetical friendly base-contact arrangement, NOT a claim about
actual army positioning. Does not produce Offence Density or alter scoring.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_explicit_support_combat import (
    ExplicitSupportContext, calculate_explicit_support_duel,
)
from offence_support_architecture_audit import validate_combat_role_allocation


def main():
    fixture = ROOT / "tests" / "fixtures" / "iron-hills-cal.json"
    result = run_analysis_workflow(str(fixture), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Real importer did not return an Army")
    army = result["army"]
    candidates = [
        e for e in army.entries
        if e.counts_as_model and e.configured_profile is not None
        and e.profile.id == "IH_WR"
    ]
    support = next(
        (e for e in candidates
         if any(w.id == "WG_SPEAR" for w in e.configured_profile.effective_wargear)),
        None,
    )
    front = next(
        (e for e in candidates
         if not any(w.id == "WG_SPEAR" for w in e.configured_profile.effective_wargear)),
        None,
    )
    if front is None or support is None:
        raise ValueError("Expected spear and non-spear Iron Hills Warrior configurations")
    role_audit = validate_combat_role_allocation(
        ["example-frontline-1", "example-support-1"],
        [{"fighter_ids": ["example-frontline-1"],
          "supporter_ids": ["example-support-1"]}],
    )
    report = calculate_explicit_support_duel(
        front.configured_profile,
        support.configured_profile,
        fighter_id="example-frontline-1",
        supporter_id="example-support-1",
        context=ExplicitSupportContext.conditional_example(),
    )
    report["model_identity_conservation"] = role_audit
    report["example_assumptions"] = [
        "Hypothetical friendly Iron Hills Warriors in base contact",
        "Supporter Infantry, unengaged, standing, has not shot",
        "Neither supporting Heroic Action nor shielding fighter",
        "Explicitly assumes standard spear support is permitted",
        "No charge, trap, Might or targeting probabilities inferred",
    ]
    print(json.dumps(report, indent=2, allow_nan=False))
    return report


if __name__ == "__main__":
    main()
