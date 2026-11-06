"""DEV-082-A3-2H-1 contract tests: no inferred supporting attacks."""
from pathlib import Path
from types import SimpleNamespace as Obj
import pytest
from offence_support_architecture_audit import (
    audit_army_support_inventory, inspect_source_contract,
    validate_combat_role_allocation, build_six_army_support_audit,
    SOURCE_CONTRACT,
)


def army():
    entries = [
        Obj(counts_as_model=True, quantity=3,
            configured_profile=Obj(
                profile=Obj(id="SPEAR"), effective_wargear=[Obj(id="WG_SPEAR"),
                                                           Obj(id="WG_HAND_WEAPON")])),
        Obj(counts_as_model=True, quantity=2,
            configured_profile=Obj(
                profile=Obj(id="SWORD"), effective_wargear=[Obj(id="WG_HAND_WEAPON")])),
        Obj(counts_as_model=False, quantity=1, configured_profile=None),
    ]
    return Obj(entries=entries, model_count=lambda: 5)


def test_spear_inventory_counts_models_not_entries():
    result = audit_army_support_inventory(army(), key="army")
    assert result["models"] == 5
    assert result["potential_support_equipped_models"] == 3


def test_spear_presence_does_not_imply_active_support():
    result = audit_army_support_inventory(army(), key="army")
    assert result["conditional_support_combats_calculated"] == 0
    assert result["entries"][0]["actual_support_role"] == "unknown"


def test_unrelated_entry_excluded_from_model_population():
    assert len(audit_army_support_inventory(army(), key="army")["entries"]) == 2


def test_source_contract_keys_present():
    assert "combat_side.py" in SOURCE_CONTRACT
    assert "combat_participant.py" in SOURCE_CONTRACT


def test_missing_source_file_explicitly_blocked(tmp_path):
    r = inspect_source_contract(tmp_path)
    assert r["status"] == "incomplete"
    assert r["source_probes"]["combat_side.py"]["status"] == "missing_file"


def test_mock_source_contract_all_present(tmp_path):
    for filename, contract in SOURCE_CONTRACT.items():
        chunks = []
        if "class" in contract:
            chunks.append("@dataclass\nclass %s:\n" % contract["class"])
            chunks.append("".join("    %s: int\n" % attr for attr in contract.get("attributes", ())))
            chunks.append("".join("    def %s(self):\n        pass\n" % prop
                                  for prop in contract.get("properties", ())))
            chunks.insert(0, "from dataclasses import dataclass\n")
        else:
            chunks.extend("def %s():\n    pass\n" % name
                          for name in contract.get("functions", ()))
        (tmp_path / filename).write_text("".join(chunks), encoding="utf-8")
    assert inspect_source_contract(tmp_path)["status"] == "verified"


def test_missing_combat_side_property_detected(tmp_path):
    for filename, contract in SOURCE_CONTRACT.items():
        if contract.get("class"):
            (tmp_path / filename).write_text("class %s:\n    pass\n" % contract["class"])
        else:
            (tmp_path / filename).write_text("".join("def %s():\n    pass\n" % n
                                                     for n in contract.get("functions", ())))
    result = inspect_source_contract(tmp_path)
    assert "strike_participants" in result["source_probes"]["combat_side.py"]["missing"]


def test_one_fighter_one_supporter_identity_allocation():
    r = validate_combat_role_allocation(["A", "B", "C"], [
        {"fighter_ids": ["A"], "supporter_ids": ["B"]},
    ])
    assert (r["fighters"], r["supporters"], r["unallocated_models"]) == (1, 1, 1)
    assert r["score"] is None
    assert r["support_legality_verified"] is False


def test_two_independent_fighters():
    r = validate_combat_role_allocation(["A", "B"], [
        {"fighter_ids": ["A", "B"], "supporter_ids": []},
    ])
    assert r["allocated_models"] == 2


@pytest.mark.parametrize("combats", [
    [{"fighter_ids": [], "supporter_ids": ["A"]}],
    [{"fighter_ids": ["A"], "supporter_ids": ["A"]}],
    [{"fighter_ids": ["A"], "supporter_ids": ["C"]}],
    [{"fighter_ids": ["A"], "supporter_ids": []},
     {"fighter_ids": ["A"], "supporter_ids": []}],
    [{"fighter_ids": ["A"], "supporter_ids": ["B"]},
     {"fighter_ids": ["B"], "supporter_ids": []}],
])
def test_invalid_combat_allocation_rejected(combats):
    with pytest.raises(ValueError):
        validate_combat_role_allocation(["A", "B"], combats)


def test_duplicate_roster_ids_rejected():
    with pytest.raises(ValueError):
        validate_combat_role_allocation(["A", "A"], [])


def test_blank_roster_id_rejected():
    with pytest.raises(ValueError):
        validate_combat_role_allocation([""], [])


def test_inventory_mismatched_count_rejected():
    a = army()
    a.model_count = lambda: 4
    with pytest.raises(ValueError):
        audit_army_support_inventory(a, key="test")


def test_incomplete_cohort_keeps_failed_army(tmp_path):
    result = build_six_army_support_audit(
        fixtures=[("a", "one"), ("b", "two")],
        loader=lambda name: army() if name == "one" else 1 / 0,
        src_dir=tmp_path,
    )
    assert result["armies_audited"] == 1
    assert result["rows"][1]["status"] == "blocked"
    assert result["validation_status"] == "incomplete"


def test_no_candidate_score_or_calibration_changes(tmp_path):
    r = build_six_army_support_audit(
        fixtures=[("a", "one")], loader=lambda _: army(), src_dir=tmp_path,
    )
    assert r["candidate_raw_density"] is None
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False
    assert r["dashboard_score"] is None


def test_no_default_support_assigned_with_war_spear():
    a = army()
    a.entries[0].configured_profile.effective_wargear.append(Obj(id="WG_WAR_SPEAR"))
    r = audit_army_support_inventory(a, key="x")
    assert r["potential_support_equipped_models"] == 3
    assert r["entries"][0]["actual_support_role"] == "unknown"


def test_no_models_zero_population_allowed():
    a = Obj(entries=[], model_count=lambda: 0)
    r = audit_army_support_inventory(a, key="x")
    assert r["models"] == 0


def test_no_combat_allocations_remain_unallocated():
    r = validate_combat_role_allocation(["A", "B"], [])
    assert r["unallocated_models"] == 2
    assert r["no_double_counting_verified"] is True
