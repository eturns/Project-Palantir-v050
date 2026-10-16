import json
from pathlib import Path

folder = Path("docs/validation/dev073")

files = {
    "Five Armies": "dev073c_five_armies_validation.json",
    "Dale": "dev073c_garrison_of_dale_validation.json",
    "Iron Hills": "dev073b_iron_hills_validation.json",
    "Dol Guldur": "dev073b_dol_guldur_validation.json",
}

armies = {
    name: json.loads((folder / filename).read_text())
    for name, filename in files.items()
}

print("Army | Points | Models | Presence benchmark")
for name, data in armies.items():
    print(
        name,
        data["army"]["points"],
        data["army"]["models"],
        f'{data["benchmarks"]["presence"]:.6f}',
        sep=" | ",
    )

print("\nScenario | " + " | ".join(armies))

scenario_ids = [
    scenario["id"]
    for scenario in armies["Five Armies"]["scenarios"]
]

for scenario_id in scenario_ids:
    scores = []

    for data in armies.values():
        scenario = next(
            item
            for item in data["scenarios"]
            if item["id"] == scenario_id
        )
        scores.append(f'{scenario["score"]:.6f}')

    print(scenario_id + " | " + " | ".join(scores))

    print("\nScenario calculation audit")

for name, data in armies.items():
    failures = []

    for scenario in data["scenarios"]:
        demands = scenario["demands"]
        expected = sum(
            demand["capability"]
            for demand in demands
        ) / len(demands)

        if abs(scenario["score"] - expected) > 1e-10:
            failures.append(scenario["id"])

    print(
        name,
        "checked=", len(data["scenarios"]),
        "calculation_failures=", len(failures),
        "failed_ids=", failures,
    )

    print("\nCross-army capability audit")

probes = {
    "Distributed control": ("DOMINATION", "distributed_control"),
    "Concentrated control": ("DESTROY_THE_SUPPLIES", "concentrated_control"),
    "Mobility": ("RECONNOITRE", "mobility"),
    "Projection": ("CLASH_BY_MOONLIGHT", "projection"),
    "Attrition output": ("TO_THE_DEATH", "attrition_output"),
    "Key-model pressure": ("ASSASSINATION", "key_model_pressure"),
    "Key-model preservation": ("LEAD_FROM_THE_FRONT", "key_model_preservation"),
    "State resilience": ("TO_THE_DEATH", "state_resilience"),
    "Deployment recovery": ("HOLD_GROUND", "deployment_recovery"),
}

print("Capability | " + " | ".join(armies))

for label, (scenario_id, dimension) in probes.items():
    values = []

    for data in armies.values():
        scenario = next(
            item for item in data["scenarios"]
            if item["id"] == scenario_id
        )
        demand = next(
            item for item in scenario["demands"]
            if item["dimension"] == dimension
        )
        values.append(f'{demand["capability"]:.6f}')

    print(label + " | " + " | ".join(values))

    print("\nScenario override audit")

checks = {
    "HEIRLOOM_OF_AGES_PAST": "object_interaction",
    "SEIZE_THE_PRIZES": "object_interaction",
    "RETRIEVAL": "object_interaction",
    "FOG_OF_WAR": "key_model_preservation",
    "LEAD_FROM_THE_FRONT": "key_model_preservation",
}

print("Scenario / capability | " + " | ".join(armies))

for scenario_id, dimension in checks.items():
    values = []

    for data in armies.values():
        scenario = next(
            item for item in data["scenarios"]
            if item["id"] == scenario_id
        )
        demand = next(
            item for item in scenario["demands"]
            if item["dimension"] == dimension
        )
        values.append(f'{demand["capability"]:.6f}')

    print(
        f"{scenario_id} / {dimension}"
        + " | "
        + " | ".join(values)
    )