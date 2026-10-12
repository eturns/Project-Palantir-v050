"""DEV-077S-I2-D-C1: profile-level mobility comparison, read-only.

Run at repository root: py -3.14 tools/i2d_c1_mobility_profiles.py
Uses current source CSV profiles, rule assignments and legacy mobility weights.
Does NOT infer configured mounts, battlefield positions, or actual army rosters.
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "data/profiles/dol_guldur_profiles.csv"
RULES = ROOT / "data/profiles/profile_special_rules.csv"
TAGS = ROOT / "data/rules/special_rule_tags.csv"

CANDIDATES = ("DG_NEC","DG_LS","DG_AK","DG_MGS","DG_MHS","DG_WK","DG_HOW","DG_FW")
NO_TERRAIN_PENALTY = {"SPECTRAL_WALK", "SWIFT_MOVEMENT"}
ANCHOR = "SPIRITUAL_DISPLACEMENT"


def records(path):
    with path.open("r", newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def movement_number(raw):
    return float(str(raw).replace('"', "").strip())


def profile_snapshot(profile, rule_ids, weights):
    move = movement_number(profile["movement"])
    base = float(profile["base_size_mm"])
    if base <= 0:
        raise ValueError("Base size must be positive")
    open_score = move / math.sqrt(base / 25)
    difficult_score = open_score if rule_ids & NO_TERRAIN_PENALTY else open_score / 2
    # The existing legacy bonus excludes Spiritual Displacement as an individual
    # bonus: pairing is an army-level effect, not a profile-level score.
    legacy_bonus = sum(weights.get(rule, 0) for rule in rule_ids if rule != ANCHOR)
    return {
        "id": profile["id"], "name": profile["name"],
        "move_inches": move, "base_mm": int(base),
        "open_score": round(open_score, 4),
        "difficult_score": round(difficult_score, 4),
        "legacy_rule_bonus": round(legacy_bonus, 4),
        "illustrative_legacy": round(open_score + legacy_bonus, 4),
        "self_reposition": "UNNATURAL_SPEED" in rule_ids,
        "partner_reposition": ANCHOR in rule_ids,
        "rules": "|".join(sorted(rule_ids)),
        "limitation": "Unconfigured base profile; pair and battlefield positions unmodelled",
    }


def build_rows():
    profiles = {r["id"]: r for r in records(PROFILES)}
    assigned = {}
    for row in records(RULES):
        assigned.setdefault(row["profile_id"], set()).add(row["rule_id"])
    weights = {}
    for row in records(TAGS):
        if row["ability_tag_id"] == "MOBILITY":
            weights[row["special_rule_id"]] = float(row["weight"])
    return [profile_snapshot(profiles[i], assigned.get(i, set()), weights) for i in CANDIDATES]


def main():
    rows = build_rows()
    out = ROOT / "i2d_c1_profile_mobility_comparison.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Created {out}")
    print("ID       OPEN     TERRAIN   LEGACY*   NOTES")
    for r in rows:
        notes = ("self reposition; " if r["self_reposition"] else "") + (
            "partner required; " if r["partner_reposition"] else ""
        )
        print(f'{r["id"]:8} {r["open_score"]:7.3f} {r["difficult_score"]:9.3f} {r["illustrative_legacy"]:9.3f}   {notes}')
    print("*Illustrative unconfigured profile value, not final whole-army metric.")


if __name__ == "__main__":
    main()
