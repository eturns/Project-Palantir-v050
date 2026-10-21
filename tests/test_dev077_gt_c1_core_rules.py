"""DEV-077-GT-C1: sourced Goblin-town rule registration and reuse tests."""
import csv
from pathlib import Path
import pytest
from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from chittering_hordes_support import (
    has_chittering_hordes, can_chittering_hordes_support,
    make_chittering_hordes_support_participant,
)

ROOT=Path(__file__).resolve().parents[1]
EXPECTED={
    "GT_KING":{"BURLY","CAVE_DWELLER","RESISTANT_TO_MAGIC","TERROR","RELENTLESS_ADVANCE"},
    "GT_GRINNAH":{"CAVE_DWELLER","CHITTERING_HORDES"},
    "GT_SCRIBE":set(),
    "GT_CAPTAIN":{"CAVE_DWELLER","CHITTERING_HORDES"},
    "GT_GOLLUM":{"CAVE_DWELLER","MOUNTAIN_DWELLER","STALK_UNSEEN"},
    "GT_WARRIOR":{"CAVE_DWELLER","CHITTERING_HORDES"},
}

@pytest.fixture(scope="module")
def profiles():
    profiles={p.id:p for p in load_all_profiles()}
    load_profile_special_rules(profiles,load_special_rules())
    return profiles

def test_all_six_profiles_load(profiles):
    assert EXPECTED.keys() <= profiles.keys()

@pytest.mark.parametrize("profile_id",list(EXPECTED))
def test_intrinsic_core_rule_assignments(profiles,profile_id):
    actual={a.rule.id for a in profiles[profile_id].special_rules}
    assert EXPECTED[profile_id] <= actual

def test_shared_chittering_hordes_is_reusable(profiles):
    warrior=ConfiguredProfile(profiles["GT_WARRIOR"])
    captain=ConfiguredProfile(profiles["GT_CAPTAIN"])
    assert has_chittering_hordes(warrior)
    assert can_chittering_hordes_support(warrior,captain,valid_support_position=True)
    support=make_chittering_hordes_support_participant(
        warrior,captain,valid_support_position=True)
    assert support.duel_dice==1 and not support.can_make_strikes

def test_no_support_without_verified_position(profiles):
    warrior=ConfiguredProfile(profiles["GT_WARRIOR"])
    assert not can_chittering_hordes_support(
        warrior,warrior,valid_support_position=False)

def test_gollum_is_not_a_goblin_rule_holder(profiles):
    gollum=ConfiguredProfile(profiles["GT_GOLLUM"])
    assert not has_chittering_hordes(gollum)

def test_rule_catalogue_has_no_duplicate_ids():
    path=ROOT/"data/rules/special_rules.csv"
    with path.open(encoding="utf-8-sig",newline="") as handle:
        ids=[r["id"] for r in csv.DictReader(handle)]
    assert len(ids)==len(set(ids))
