import csv

from siege_engine_profile import SiegeEngineProfile


def load_siege_engine_profiles(
    file_path: str = (
        "data/profiles/siege_engine_profiles.csv"
    ),
) -> dict[str, SiegeEngineProfile]:
    """
    Loads canonical Siege Engine Profiles.
    """

    profiles: dict[str, SiegeEngineProfile] = {}

    with open(
        file_path,
        newline="",
        encoding="utf-8",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            profile = SiegeEngineProfile(
                id=row["id"],
                name=row["name"],
                points=int(row["points"]),
                range_min=int(row["range_min"]),
                range_max=int(row["range_max"]),
                strength=int(row["strength"]),
                defence=int(row["defence"]),
                wounds=int(row["wounds"]),
                base_size_mm=int(
                    row["base_size_mm"]
                ),
                size=row["size"],
            )

            if profile.id in profiles:
                raise ValueError(
                    "Duplicate Siege Engine Profile ID: "
                    f"{profile.id}"
                )

            profiles[profile.id] = profile

    return profiles