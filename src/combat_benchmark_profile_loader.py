import csv

from profiles import Profile


COMBAT_BENCHMARK_PROFILE_FILE = (
    "data/test_profiles/combat_benchmark_profiles.csv"
)


def load_combat_benchmark_profiles() -> list[Profile]:
    profiles = []

    with open(
        COMBAT_BENCHMARK_PROFILE_FILE,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            profiles.append(
                Profile(
                    id=row["id"],
                    name=row["name"],
                    points=int(row["points"]),
                    movement=int(
                        row["movement"].replace('"', "")
                    ),
                    base_size_mm=int(row["base_size_mm"]),
                    fight=int(row["fight"]),
                    shooting=row["shooting"],
                    strength=int(row["strength"]),
                    defence=int(row["defence"]),
                    attacks=int(row["attacks"]),
                    wounds=int(row["wounds"]),
                    courage=row["courage"],
                    intelligence=row["intelligence"],
                    might=int(row["might"]),
                    will=int(row["will"]),
                    fate=int(row["fate"]),
                    max_in_army=int(row["max_in_army"]),
                )
            )

    return profiles