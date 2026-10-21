"""Project Palantír — load canonical MESBG profiles from CSV."""
import csv

from profiles import Profile
from profile_classification import HeroicStatus, ModelType

PROFILE_FILES = (
    "data/profiles/dol_guldur_profiles.csv",
    "data/profiles/iron_hills_profiles.csv",
    "data/profiles/lake_town_profiles.csv",
    "data/profiles/gundabad_profiles.csv",
    "data/profiles/goblin_town_profiles.csv",
    "data/profiles/erebor_profiles.csv",
    "data/profiles/dale_profiles.csv",
    "data/profiles/beornings_profiles.csv",
    "data/profiles/mirkwood_profiles.csv",  # DEV-077S-I2-I-C3-D7-B4-B1
)


def _load_profiles_from_file(file_path: str) -> list[Profile]:
    profiles = []
    with open(file_path, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            profiles.append(Profile(
                id=row["id"],
                name=row["name"],
                points=int(row["points"]),
                movement=int(row["movement"].replace('"', "")),
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
                heroic_status=(HeroicStatus(row["heroic_status"])
                               if row.get("heroic_status") else None),
                model_types={ModelType(item.strip()) for item in
                             row.get("model_types", "").split("|") if item.strip()},
                races={item.strip() for item in
                       row.get("races", "").split("|") if item.strip()},
                factions={item.strip() for item in
                          row.get("factions", "").split("|") if item.strip()},
            ))
    return profiles


def load_profile(profile_id: str) -> Profile:
    for profile in load_all_profiles():
        if profile.id == profile_id:
            return profile
    raise ValueError(f"Profile '{profile_id}' not found.")


def load_all_profiles() -> list[Profile]:
    profiles = []
    profile_ids = set()
    for file_path in PROFILE_FILES:
        loaded_profiles = _load_profiles_from_file(file_path)
        for profile in loaded_profiles:
            if profile.id in profile_ids:
                raise ValueError(f"Duplicate Profile ID: {profile.id}")
            profile_ids.add(profile.id)
            profiles.append(profile)
    return profiles
