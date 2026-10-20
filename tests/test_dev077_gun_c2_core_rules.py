"""DEV-077-GUN-C2: source-verified reuse of established core rules.

The new Gundabad-specific mechanics are intentionally not claimed as implemented.
"""
import csv
from collections import Counter
from pathlib import Path

from loader import load_all_profiles
from relationship_loader import load_profile_special_rules, load_profile_heroic_actions
from rule_loader import load_special_rules, load_heroic_actions

RULE_CSV = Path('data/profiles/profile_special_rules.csv')
HERO_CSV = Path('data/profiles/profile_heroic_actions.csv')


def _rows(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


def _rules(rows, profile):
    return {(r['rule_id'], r['parameter'] or '') for r in rows if r['profile_id'] == profile}


def test_gundabad_existing_rules_match_2024_book():
    rows = _rows(RULE_CSV)
    ancient = {('ANCIENT_ENEMIES', 'DWARF'), ('ANCIENT_ENEMIES', 'ELF')}
    for pid in ('GUNDABAD_BERSERKER', 'GUNDABAD_OGRE', 'GUNDABAD_TROLL',
                'GUNDABAD_CATAPULT_TROLL', 'ORC_COMMANDER'):
        assert ancient <= _rules(rows, pid)
    expected = {
        'GUNDABAD_OGRE': {('DOMINANT', '3'), ('TERROR', '')},
        'GUNDABAD_TROLL': {('DOMINANT', '4'), ('TERROR', '')},
        'GUNDABAD_CATAPULT_TROLL': {('DOMINANT', '5'), ('TERROR', '')},
        'TROLL_BRUTE': {('DOMINANT', '5'), ('TERROR', ''), ('FEARLESS', '')},
    }
    for pid, required in expected.items():
        assert required <= _rules(rows, pid)


def test_core_rules_not_wrongly_assigned_to_ordinary_warriors():
    rows = _rows(RULE_CSV)
    for pid in ('GUNDABAD_BERSERKER', 'GOBLIN_MERCENARY',
                'GOBLIN_MERCENARY_CAPTAIN', 'WAR_BAT'):
        actual = {rule for rule, _ in _rules(rows, pid)}
        assert not actual.intersection({'DOMINANT', 'FEARLESS', 'TERROR'})


def test_gundabad_heroic_march_assignments():
    rows = _rows(HERO_CSV)
    for pid in ('GOBLIN_MERCENARY_CAPTAIN', 'ORC_COMMANDER'):
        assert [r['heroic_action_id'] for r in rows if r['profile_id'] == pid] == ['HEROIC_MARCH']


def test_new_gundabad_core_assignments_are_unique_and_catalogued():
    rows = _rows(RULE_CSV)
    affected = {'GUNDABAD_BERSERKER', 'GUNDABAD_OGRE', 'GUNDABAD_TROLL',
                'GUNDABAD_CATAPULT_TROLL', 'ORC_COMMANDER', 'TROLL_BRUTE'}
    selected = [(r['profile_id'], r['rule_id'], r['parameter'] or '')
                for r in rows if r['profile_id'] in affected]
    assert all(value == 1 for value in Counter(selected).values())
    catalog = load_special_rules()
    assert {rule_id for _, rule_id, _ in selected} <= set(catalog)


def test_production_loader_resolves_gundabad_rules_and_heroics():
    profiles = {profile.id: profile for profile in load_all_profiles()}
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    load_profile_heroic_actions(profiles=profiles, heroic_actions=load_heroic_actions())
    troll = profiles['GUNDABAD_TROLL']
    assert {(a.rule.id, a.parameter) for a in troll.special_rules} >= {
        ('ANCIENT_ENEMIES', 'DWARF'), ('ANCIENT_ENEMIES', 'ELF'),
        ('DOMINANT', 4), ('TERROR', None),
    }
    for pid in ('ORC_COMMANDER', 'GOBLIN_MERCENARY_CAPTAIN'):
        assert 'HEROIC_MARCH' in {action.id for action in profiles[pid].heroic_actions}
