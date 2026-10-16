"""Focused Mirkwood profile-rule registration checks. No army-list rules."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def records(relative_path):
    with (ROOT / relative_path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))

EXPECTED = {
    "MW_LEGOLAS": {"LEADER_PALACE_GUARD", "SHARPSHOOTER", "WOODLAND_CREATURE", "DEADLY_SHOT", "PINPOINT_SHOT"},
    "MW_TAURIEL": {"EXPERT_SHOT", "SHARPSHOOTER", "WOODLAND_CREATURE", "BLADE_MISTRESS", "VENGEFUL_FURY"},
    "MW_RANGER_CAPTAIN": {"SHARPSHOOTER", "WOODLAND_CREATURE", "KNIFE_FIGHTER"},
    "MW_RANGER": {"SHARPSHOOTER", "WOODLAND_CREATURE", "KNIFE_FIGHTER"},
}
HEROICS = {
    "MW_LEGOLAS": {"HEROIC_ACCURACY", "HEROIC_STRIKE"},
    "MW_TAURIEL": {"HEROIC_ACCURACY", "HEROIC_STRIKE"},
    "MW_RANGER_CAPTAIN": {"HEROIC_ACCURACY"},
}

def test_required_rule_definitions():
    ids = [r["id"] for r in records("data/rules/special_rules.csv")]
    assert set.union(*EXPECTED.values()) <= set(ids)

def test_rule_identifiers_unique_for_mirkwood():
    ids = [r["id"] for r in records("data/rules/special_rules.csv")]
    for rid in set.union(*EXPECTED.values()):
        assert ids.count(rid) == 1, rid

def test_exact_profile_assignments():
    actual = {name: [] for name in EXPECTED}
    for row in records("data/profiles/profile_special_rules.csv"):
        if row["profile_id"] in actual:
            actual[row["profile_id"]].append(row["rule_id"])
    for name, rules in EXPECTED.items():
        assert set(actual[name]) == rules
        assert len(actual[name]) == len(rules)

def test_profile_rule_parameters_blank():
    for row in records("data/profiles/profile_special_rules.csv"):
        if row["profile_id"] in EXPECTED:
            assert not (row.get("parameter") or "").strip()

def test_profile_heroic_actions():
    actual = {name: [] for name in (*HEROICS, "MW_RANGER")}
    for row in records("data/profiles/profile_heroic_actions.csv"):
        if row["profile_id"] in actual:
            actual[row["profile_id"]].append(row["heroic_action_id"])
    for name, expected in HEROICS.items():
        assert set(actual[name]) == expected
        assert len(actual[name]) == len(expected)
    assert actual["MW_RANGER"] == []

def test_heroic_action_ids_exist():
    available = {r["id"] for r in records("data/rules/heroic_actions.csv")}
    assert set.union(*HEROICS.values()) <= available

def test_no_army_rule_files_modified_by_stage():
    # Registration is scoped to profile-level records; army-list effects
    # intentionally have no representation in EXPECTED.
    assert "KNIFE_MASTERY" not in set.union(*EXPECTED.values())
    assert "CLEAR_THE_NESTS" not in set.union(*EXPECTED.values())

def test_legacy_sharpshooter_preserved():
    ids = [r["id"] for r in records("data/rules/special_rules.csv")]
    assert "SHARPSHOOTER" in ids
