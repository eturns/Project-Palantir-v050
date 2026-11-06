"""DEV-082-A3-2H-3 — Iron Hills explicitly hypothetical joint kill example."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from main import run_analysis_workflow
from offence_explicit_support_combat import ExplicitSupportContext
from offence_joint_support_wounds import calculate_explicit_joint_support_kill
from offence_support_architecture_audit import validate_combat_role_allocation


def main():
    fixture = ROOT / "tests" / "fixtures" / "iron-hills-cal.json"
    result = run_analysis_workflow(str(fixture), print_report=False)
    if not isinstance(result, dict) or result.get("army") is None:
        raise ValueError("Real importer did not return Army")
    army = result["army"]
    warriors = [entry for entry in army.entries
                if entry.counts_as_model
                and entry.configured_profile is not None
                and entry.profile.id == "IH_WR"]
    spear = next((entry for entry in warriors
                  if any(w.id == "WG_SPEAR"
                         for w in entry.configured_profile.effective_wargear)), None)
    front = next((entry for entry in warriors
                  if not any(w.id == "WG_SPEAR"
                             for w in entry.configured_profile.effective_wargear)), None)
    if spear is None or front is None:
        raise ValueError("Expected spear and non-spear Iron Hills Warriors")
    fighter_id, supporter_id = "example-frontline-1", "example-support-1"
    allocation = validate_combat_role_allocation(
        [fighter_id, supporter_id],
        [{"fighter_ids": [fighter_id], "supporter_ids": [supporter_id]}],
    )
    output = calculate_explicit_joint_support_kill(
        front.configured_profile,
        spear.configured_profile,
        fighter_id=fighter_id, supporter_id=supporter_id,
        context=ExplicitSupportContext.conditional_example(),
    )
    output["identity_conservation"] = allocation
    output["scenario_scope"] = ("hypothetical standing Infantry spear support, "
                                "uncharged, untrapped, benchmark single wound")
    print(json.dumps(output, indent=2, allow_nan=False))
    return output


if __name__ == "__main__":
    main()
