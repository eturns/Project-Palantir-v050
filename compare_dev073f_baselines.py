import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIRECTORY = ROOT / "docs" / "validation" / "dev073"

FIXTURES = {
    "Five Armies": (
        "five_armies_baseline.json",
        "dev073f_five_armies_validation.json",
    ),
    "Garrison of Dale": (
        "garrison_of_dale_baseline.json",
        "dev073f_garrison_of_dale_validation.json",
    ),
    "Iron Hills": (
        "iron_hills_baseline.json",
        "dev073f_iron_hills_validation.json",
    ),
    "Dol Guldur": (
        "dol_guldur_700_baseline.json",
        "dev073f_dol_guldur_700_validation.json",
    ),
}

for army_name, (baseline_name, revised_name) in FIXTURES.items():
    baseline = json.loads((DIRECTORY / baseline_name).read_text())
    revised = json.loads((DIRECTORY / revised_name).read_text())

    assert baseline["fixture_sha256"] == revised["fixture_sha256"]
    assert baseline["army"]["points"] == revised["army"]["points"]
    assert baseline["army"]["models"] == revised["army"]["models"]

    old_scenarios = {
        scenario["id"]: scenario
        for scenario in baseline["scenarios"]
    }
    new_scenarios = {
        scenario["id"]: scenario
        for scenario in revised["scenarios"]
    }

    assert old_scenarios.keys() == new_scenarios.keys()
    assert len(old_scenarios) == 24

    changes = []

    for scenario_id, old in old_scenarios.items():
        new = new_scenarios[scenario_id]
        difference = new["score"] - old["score"]

        if abs(difference) > 1e-10:
            changes.append(
                (scenario_id, old["score"], new["score"], difference)
            )

    print(f"\n{army_name}")
    print(f"  Points: {revised['army']['points']}")
    print(f"  Models: {revised['army']['models']}")
    print(f"  Changed scenarios: {len(changes)}/24")

    for scenario_id, old_score, new_score, difference in sorted(
        changes,
        key=lambda item: abs(item[3]),
        reverse=True,
    )[:5]:
        print(
            f"  {scenario_id}: "
            f"{old_score:.6f} -> {new_score:.6f} "
            f"({difference:+.6f})"
        )

CHECKS = {
    "Iron Hills": ("FOG_OF_WAR", "HEIRLOOM_OF_AGES_PAST"),
    "Dol Guldur": ("LEAD_FROM_THE_FRONT", "CLASH_BY_MOONLIGHT"),
}

for army_name, scenario_ids in CHECKS.items():
    baseline_name, revised_name = FIXTURES[army_name]

    baseline = json.loads((DIRECTORY / baseline_name).read_text())
    revised = json.loads((DIRECTORY / revised_name).read_text())

    old_scenarios = {
        scenario["id"]: scenario
        for scenario in baseline["scenarios"]
    }
    new_scenarios = {
        scenario["id"]: scenario
        for scenario in revised["scenarios"]
    }

    for scenario_id in scenario_ids:
        old = old_scenarios[scenario_id]
        new = new_scenarios[scenario_id]

        print(f"\n{army_name} — {scenario_id}")
        print(f"Score: {old['score']:.6f} -> {new['score']:.6f}")

        old_demands = {
            demand["dimension"]: demand
            for demand in old["demands"]
        }
        new_demands = {
            demand["dimension"]: demand
            for demand in new["demands"]
        }

        for dimension in sorted(
            old_demands.keys() | new_demands.keys()
        ):
            before = old_demands.get(dimension)
            after = new_demands.get(dimension)

            if before is None or after is None:
                print(f"  {dimension}: demand added or removed")
                continue

            print(
                f"  {dimension}: "
                f"capability {before['capability']:.6f} "
                f"-> {after['capability']:.6f}; "
                f"intensity {before['intensity']:.6f} "
                f"-> {after['intensity']:.6f}"
            )