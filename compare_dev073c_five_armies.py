import json
from pathlib import Path

folder = Path("docs/validation/dev073")

original = json.loads(
    (folder / "garrison_of_dale_baseline.json").read_text()
)
corrected = json.loads(
    (folder / "dev073c_garrison_of_dale_validation.json").read_text()
)

print(
    "Fixture hashes match:",
    original["fixture_sha256"] == corrected["fixture_sha256"],
)
print(
    "Scenario counts:",
    len(original["scenarios"]),
    len(corrected["scenarios"]),
)

original_by_id = {
    scenario["id"]: scenario
    for scenario in original["scenarios"]
}

changed = 0

for scenario in corrected["scenarios"]:
    previous = original_by_id[scenario["id"]]

    if abs(scenario["score"] - previous["score"]) > 0.000001:
        changed += 1
        print(
            scenario["id"],
            f'{previous["score"]:.6f}',
            "->",
            f'{scenario["score"]:.6f}',
        )
        previous_demands = {
            demand["dimension"]: demand["capability"]
            for demand in previous["demands"]
        }

        for demand in scenario["demands"]:
            dimension = demand["dimension"]
            old_value = previous_demands[dimension]
            new_value = demand["capability"]

            if abs(new_value - old_value) > 0.000001:
                print(
                    "  Changed capability:",
                    dimension,
                    f"{old_value:.6f}",
                    "->",
                    f"{new_value:.6f}",
                )

print("Changed scenario scores:", changed)