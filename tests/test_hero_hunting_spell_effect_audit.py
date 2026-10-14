import csv
from pathlib import Path
import pytest

from hero_hunting_spell_effect_audit import (
    HeroHuntingSpellEffect, audit_canonical_spell_effects,
    require_verified_spell_effect,
)


def test_all_nine_canonical_spells_are_inventoried():
    rows = audit_canonical_spell_effects()
    assert len(rows) == 9
    assert len({r.spell_id for r in rows}) == 9


def test_necromancer_assignments_retain_cast_values():
    rows = audit_canonical_spell_effects()
    actual = {r.spell_id: r.assigned_profiles for r in rows}
    assert actual["CHILL_SOUL"] == (("DG_NEC", 5),)
    assert actual["TRANSFIX"] == (("DG_NEC", 3),)


def test_offence_category_does_not_prove_direct_damage():
    row = next(r for r in audit_canonical_spell_effects() if r.spell_id == "CHILL_SOUL")
    assert row.rule_category == "OFFENCE"
    assert row.effect == HeroHuntingSpellEffect.UNVERIFIED
    assert not row.effect_mechanically_verified


def test_command_category_does_not_prove_hero_disabling():
    row = next(r for r in audit_canonical_spell_effects() if r.spell_id == "COMPEL")
    assert row.rule_category == "COMMAND"
    assert row.effect is HeroHuntingSpellEffect.UNVERIFIED


def test_all_effects_fail_closed_before_inclusion_in_hero_hunting():
    for row in audit_canonical_spell_effects():
        assert row.elimination_probability is None
        with pytest.raises(ValueError, match="not mechanically verified"):
            require_verified_spell_effect(row)


def test_duplicate_spell_catalogue_rejected(tmp_path):
    file = tmp_path / "spells.csv"
    file.write_text("id,name,category\nA,First,OFFENCE\nA,Second,OFFENCE\n")
    assignment = tmp_path / "assignments.csv"
    assignment.write_text("profile_id,spell_id,cast_value\nP,A,3\n")
    with pytest.raises(ValueError, match="unique"):
        audit_canonical_spell_effects(spells_path=file, assignments_path=assignment)


def test_orphan_assignment_rejected(tmp_path):
    spells = tmp_path / "spells.csv"
    spells.write_text("id,name,category\nA,First,OFFENCE\n")
    assignments = tmp_path / "assignments.csv"
    assignments.write_text("profile_id,spell_id,cast_value\nP,B,3\n")
    with pytest.raises(ValueError, match="unknown assigned spell"):
        audit_canonical_spell_effects(spells_path=spells, assignments_path=assignments)
