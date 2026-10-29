"""DEV-077-SMAUG-C1: validate imported generic Smaug rules and geometry evidence."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def records(path):
    with (ROOT / path).open(newline='', encoding='utf-8-sig') as stream:
        return list(csv.DictReader(stream))

def test_smaug_nine_generic_rule_assignments():
    assignments = [r for r in records('data/profiles/profile_special_rules.csv') if r['profile_id'] == 'SMAUG']
    expected = {'ANCIENT_ENEMIES': 'Dwarf', 'DOMINANT': '20', 'FEARLESS': '', 'FLY': '', 'HARBINGER_OF_EVIL': '18', 'LARGE_TARGET': '', 'MONSTROUS_CHARGE': '', 'RESISTANT_TO_MAGIC': '', 'TERROR': ''}
    for key, value in expected.items():
        matches = [r for r in assignments if r['rule_id'] == key]
        assert len(matches) == 1, key
        assert matches[0]['parameter'] == value, key

def test_smaug_generic_rule_ids_are_registered():
    rule_ids = [r['id'] for r in records('data/rules/special_rules.csv')]
    assert len(rule_ids) == len(set(rule_ids))
    assert {'ANCIENT_ENEMIES', 'DOMINANT', 'FEARLESS', 'FLY', 'HARBINGER_OF_EVIL', 'LARGE_TARGET', 'MONSTROUS_CHARGE', 'RESISTANT_TO_MAGIC', 'TERROR'} <= set(rule_ids)

def test_smaug_oval_dimensions_are_explicit_and_not_a_circle():
    rows = records('data/profiles/smaug_base_geometry.csv')
    assert rows == [{'profile_id': 'SMAUG', 'shape': 'oval', 'major_axis_mm': '231', 'minor_axis_mm': '133'}]

def test_smaug_fly_uses_existing_2024_flight_mode():
    from relationship_loader import load_profile_special_rules
    from rule_loader import load_special_rules
    from configured_profile import ConfiguredProfile
    from flying_movement import flight_movement, FlightMode
    # Load a fresh profile, avoiding any global mutation or duplicate assignment.
    # Relationship loader validates every assignment against the complete loaded profile set.
    from loader import load_all_profiles
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    cfg = ConfiguredProfile(profile=profiles['SMAUG'])
    assert flight_movement(cfg, FlightMode.FLY).distance_inches == 12.0
    assert flight_movement(cfg, FlightMode.GROUND).distance_inches == 4.0
