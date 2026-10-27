"""DEV-077-TT-D1A registration contracts (no unearned mechanical claims)."""
from pathlib import Path
import csv
import sys
import pytest

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'src'))
TROLLS=('TT_BILL','TT_BERT','TT_TOM')

def rows(rel):
 with (ROOT/rel).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

@pytest.mark.parametrize('pid,value',[('TT_BILL','5'),('TT_BERT','3'),('TT_TOM','3')])
def test_dominant(pid,value):
 assert any(r['profile_id']==pid and r['rule_id']=='DOMINANT' and r['parameter']==value for r in rows('data/profiles/profile_special_rules.csv'))

@pytest.mark.parametrize('pid',TROLLS)
def test_common_rules(pid):
 actual={r['rule_id'] for r in rows('data/profiles/profile_special_rules.csv') if r['profile_id']==pid}
 assert {'DOMINANT','TERROR','LARGE_TARGET','THROW_STONES','KEEP_EM_FOR_LATER'}<=actual

@pytest.mark.parametrize('pid',TROLLS)
def test_hand_weapon(pid):
 assert any(r['profile_id']==pid and r['wargear_id']=='WG_HAND_WEAPON' for r in rows('data/profiles/profile_default_wargear.csv'))

@pytest.mark.parametrize('pid,expected',[('TT_BILL',{'HEROIC_CHALLENGE','HEROIC_STRIKE'}),('TT_BERT',{'HEROIC_DEFENCE','HEROIC_STRENGTH'}),('TT_TOM',{'HEROIC_DEFENCE'})])
def test_heroics(pid,expected):
 actual={r['heroic_action_id'] for r in rows('data/profiles/profile_heroic_actions.csv') if r['profile_id']==pid}
 assert actual==expected

def test_catalogue_has_unique_rule_records():
 ids={r['id'] for r in rows('data/rules/special_rules.csv')}
 assert {'LARGE_TARGET','THROW_STONES','KEEP_EM_FOR_LATER','MINCE_EM_FINE','ROAST_EM_SLOWLY','LINGERING_COLD','SQUASH_EM_INTO_JELLY'}<=ids

def test_unique_profile_assignments():
 records={(r['profile_id'],r['rule_id']) for r in rows('data/profiles/profile_special_rules.csv')}
 assert {('TT_BILL','MINCE_EM_FINE'),('TT_BERT','ROAST_EM_SLOWLY'),('TT_TOM','LINGERING_COLD'),('TT_TOM','SQUASH_EM_INTO_JELLY')}<=records

def test_no_unique_model_type():
 profiles=rows('data/profiles/three_trolls_profiles.csv')
 assert {r['id'] for r in profiles}==set(TROLLS)
 assert all('UNIQUE' not in r['model_types'].split('|') and r['max_in_army']=='1' for r in profiles)
