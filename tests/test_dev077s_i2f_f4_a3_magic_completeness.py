"""F4-A3: missing spell data must not be mistaken for no Magic."""
import csv

import pytest

from army import Army
from loader import load_all_profiles
from mechanical_magic_completeness import audit_army_magic_completeness
from relationship_loader import load_profile_spells
from rule_loader import load_spells


def make_army(profiles):
    army = Army()
    for profile in profiles:
        army.add_profile(profile)
    return army


def test_unhydrated_necromancer_is_not_complete():
    nec = next(p for p in load_all_profiles() if p.id == "DG_NEC")
    result = audit_army_magic_completeness(make_army([nec]))
    assert result.status == "incomplete"
    assert not result.is_complete
    assert len(result.missing) == 9
    assert ("DG_NEC", "COMPEL", 3) in result.missing
    assert result.present_assignment_count == 0


def test_canonical_relationships_restore_complete_evidence():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_spells(profiles, load_spells())
    result = audit_army_magic_completeness(make_army([profiles["DG_NEC"]]))
    assert result.status == "complete"
    assert result.expected_assignment_count == 9
    assert result.present_assignment_count == 9
    assert result.missing == result.unexpected == ()


def test_canonical_nonspellcaster_is_not_false_failure():
    profiles = {p.id: p for p in load_all_profiles()}
    profile = next(p for p in profiles.values()
                   if p.id != "DG_NEC" and not p.spells)
    result = audit_army_magic_completeness(make_army([profile]))
    assert result.is_complete
    assert result.expected_assignment_count == 0


def test_real_mixed_army_fails_when_necromancer_unhydrated():
    profiles = {p.id: p for p in load_all_profiles()}
    other = next(p for p in profiles.values() if p.id != "DG_NEC")
    result = audit_army_magic_completeness(
        make_army([profiles["DG_NEC"], other])
    )
    assert result.status == "incomplete"
    assert any(pid == "DG_NEC" for pid, _, _ in result.missing)


def test_empty_army_has_no_false_magic_incompleteness():
    result = audit_army_magic_completeness(Army())
    assert result.is_complete
    assert result.expected_assignment_count == 0


def test_status_is_diagnostic_only():
    profile = next(p for p in load_all_profiles() if p.id == "DG_NEC")
    result = audit_army_magic_completeness(make_army([profile]))
    assert result.dashboard_score is None
    assert result.scenario_score is None
    assert result.evidence_status == "diagnostic_not_calibrated"


def test_invalid_army_rejected():
    with pytest.raises(TypeError, match="Army"):
        audit_army_magic_completeness(object())


@pytest.mark.parametrize("header", [
    "profile_id,spell_id", "profile_id,cast_value", "spell_id,cast_value"
])
def test_missing_csv_columns_rejected(tmp_path, header):
    path = tmp_path / "bad.csv"
    path.write_text(header + "\n", encoding="utf8")
    with pytest.raises(ValueError, match="mandatory columns"):
        audit_army_magic_completeness(Army(), assignments_path=path)


def test_missing_csv_file_raises_not_zero(tmp_path):
    with pytest.raises(FileNotFoundError):
        audit_army_magic_completeness(
            Army(), assignments_path=tmp_path / "missing.csv"
        )


def test_invalid_threshold_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("profile_id,spell_id,cast_value\nDG_NEC,COMPEL,7\n")
    with pytest.raises(ValueError, match="cast value"):
        audit_army_magic_completeness(Army(), assignments_path=path)


def test_duplicate_rows_rejected(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text(
        "profile_id,spell_id,cast_value\nDG_NEC,COMPEL,3\nDG_NEC,COMPEL,3\n"
    )
    with pytest.raises(ValueError, match="duplicate canonical"):
        audit_army_magic_completeness(Army(), assignments_path=path)
