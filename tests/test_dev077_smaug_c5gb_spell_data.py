"""DEV-077-SMAUG-C5G-B: canonical Smaug spell-data acceptance.
Edward Turns (Project Lead).
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def test_foil_magic_defined_once_in_catalogue():
    actual = [r for r in rows('data/rules/spells.csv') if r['id'] == 'FOIL_MAGIC']
    assert actual == [{'id': 'FOIL_MAGIC', 'name': 'Foil Magic', 'category': 'MAGIC'}]


def test_smaug_has_exact_canonical_spell_assignments():
    actual = {(r['spell_id'], r['cast_value']) for r in rows('data/profiles/profile_spells.csv')
              if r['profile_id'] == 'SMAUG'}
    assert actual == {('COMPEL', '3'), ('TRANSFIX', '4'), ('FOIL_MAGIC', '5')}
    assert sum(r['profile_id'] == 'SMAUG' for r in rows('data/profiles/profile_spells.csv')) == 3


def test_all_smaug_spells_reference_defined_catalogue_ids():
    valid = {r['id'] for r in rows('data/rules/spells.csv')}
    assigned = [r['spell_id'] for r in rows('data/profiles/profile_spells.csv') if r['profile_id'] == 'SMAUG']
    assert all(spell in valid for spell in assigned)


def test_smaug_spell_assignments_present_on_real_profile_after_relationship_load():
    from loader import load_all_profiles
    from relationship_loader import load_profile_spells
    from spell import Spell
    from database.rule_category import RuleCategory

    # The relationship loader processes EVERY row in profile_spells.csv, so
    # provide the complete profile index rather than just Smaug.
    profiles = {p.id: p for p in load_all_profiles()}
    smaug = profiles['SMAUG']
    spell_rows = rows('data/rules/spells.csv')
    spells = {r['id']: Spell(id=r['id'], name=r['name'], category=RuleCategory[r['category']])
              for r in spell_rows}
    load_profile_spells(profiles, spells)
    assert {(s.spell.id, s.cast_value) for s in smaug.spells} == {
        ('COMPEL', 3), ('TRANSFIX', 4), ('FOIL_MAGIC', 5)}
