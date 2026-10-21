"""DEV-077-GUN-E: read-only final evidence audit (not tournament legality).
Run: py -3.14 scripts/audit_gundabad_final.py
Does not alter source, CSVs, tests, JSON or produce repository files.
"""
from collections import Counter, defaultdict
import ast
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
SRC = ROOT / 'src'
TESTS = ROOT / 'tests'
EXPECTED = {
 'AZOG_THE_DEFILER', 'BOLG_SPAWN_OF_AZOG', 'GOBLIN_MERCENARY',
 'GOBLIN_MERCENARY_CAPTAIN', 'GUNDABAD_BERSERKER',
 'GUNDABAD_CATAPULT_TROLL', 'GUNDABAD_OGRE', 'GUNDABAD_ORC_CAPTAIN',
 'GUNDABAD_ORC_WARRIOR', 'GUNDABAD_TROLL', 'TROLL_BRUTE', 'WAR_BAT'
}
COMPONENTS = {'ORC_COMMANDER'}
INTEGRATIONS = {
 'Metal Gauntlets wound calculation': ('configured_wound_probability.py', 'gundabad_metal_gauntlets'),
 'Goblin Crew offence context': ('profile_offensive_combat_score.py', 'gundabad_goblin_crew_combat'),
 'Catapult shooting evidence': ('army_shooting_capability.py', 'gundabad_catapult_army_evidence'),
 'Troll Brute mobility evidence': ('mobility_integration_contract.py', 'gundabad_trample_movement_evidence'),
}
REQUIRED_MODULES = [
 'gundabad_metal_gauntlets', 'gundabad_goblin_crew',
 'gundabad_goblin_crew_combat', 'gundabad_catapult_shooting',
 'gundabad_catapult_army_evidence', 'gundabad_troll_brute_trample',
 'gundabad_trample_movement_evidence', 'gundabad_relentless_advance',
 'flying_movement', 'mercenary_ambush_reserve'
]

def rows(relative):
 p=DATA / relative
 if not p.is_file():
  return None
 with p.open(encoding='utf-8-sig', newline='') as f:
  return list(csv.DictReader(f))

def printed(label, value):
 print(f'  {label}: {value}')

def matching_csv(glob, id_field):
 result=defaultdict(list)
 for path in sorted((DATA / 'profiles').glob(glob)):
  with path.open(encoding='utf-8-sig', newline='') as f:
   for row in csv.DictReader(f):
    result[row.get(id_field, '')].append((path.name,row))
 return result

def names_for(text):
 try:
  tree=ast.parse(text)
 except SyntaxError:
  return '<SYNTAX ERROR>'
 return [n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]

print('DEV-077-GUN-E — READ-ONLY FINAL AUDIT')
print('Repository:',ROOT)
print('Scope: analysis-input fidelity and mechanical evidence; NOT list legality')
if not (SRC/'army.py').is_file():
 raise SystemExit('ERROR: incorrect repository root; expected src/army.py. No audit claims made.')
print('\n[ROSTER & ARMY MEMBERSHIP]')
profiles=matching_csv('*profiles.csv','id')
missing=EXPECTED - set(profiles)
duplicates={x:len(profiles[x]) for x in EXPECTED if len(profiles[x]) != 1}
printed('expected roster profile matches',f'{len(EXPECTED)-len(missing)}/{len(EXPECTED)}')
printed('missing',sorted(missing))
printed('non-unique records',duplicates)
lists=rows('factions/army_lists.csv')
links=rows('factions/army_list_profiles.csv')
if lists is None or links is None:
 printed('army list CSV', 'MISSING')
else:
 printed('army list registration',[(x['id'],x['name']) for x in lists if x.get('id')=='GUNDABAD'])
 ids=[x.get('profile_id') for x in links if x.get('army_list_id')=='GUNDABAD']
 printed('Gundabad linked IDs',len(ids))
 printed('roster IDs not linked',sorted(EXPECTED-set(ids)))
 printed('links without a profile',sorted(set(ids)-set(profiles)))
 printed('composite component linked', 'ORC_COMMANDER' in ids)

print('\n[OPTION RELATIONAL INTEGRITY]')
options=rows('profiles/profile_options.csv') or []
gundabad_opt=[x for x in options if x.get('profile_id') in EXPECTED|COMPONENTS]
selected_ids={x.get('id') for x in gundabad_opt}
printed('Gundabad definition options',len(gundabad_opt))
printed('duplicate Gundabad external option IDs',dict((k,v) for k,v in Counter(x.get('external_id') for x in gundabad_opt if x.get('external_id')).items() if v>1))
for rel in ('profile_option_wargear.csv','profile_option_mount.csv','profile_option_special_rules.csv','profile_option_state_effects.csv'):
 rr=rows('profiles/'+rel)
 if rr is None:
  printed(rel,'not present (may use another data path)')
  continue
 hits=[x for x in rr if x.get('option_id') in selected_ids]
 printed(rel+' (resolved by option_id)',len(hits))

print('\n[IMPORTED FIXTURE]')
p=TESTS/'fixtures/gundabadalloptions.json'
if not p.is_file():
 printed('fixture','MISSING')
else:
 obj=json.loads(p.read_text(encoding='utf-8-sig'))
 printed('name',obj.get('name'))
 printed('warbands',len(obj.get('warbands',[])))
 option_ids=[]
 model_ids=[]
 for w in obj.get('warbands',[]):
  for entry in ([w.get('hero')] if w.get('hero') else []) + w.get('units',[]):
   model_ids.append(entry.get('model_id'))
   option_ids.extend(x.get('id') for x in entry.get('options',[]))
 printed('source model entries',len(model_ids))
 printed('selected external option occurrences',len(option_ids))
 print('  external option IDs:',sorted(set(option_ids)))
 defined={x.get('external_id') for x in options}
 printed('selected option IDs without options definition',sorted(set(option_ids)-defined))
 print('  Note: composite-model mapping can legitimately create additional runtime profiles.')

print('\n[MECHANICAL MODULES]')
for name in REQUIRED_MODULES:
 path=SRC/(name+'.py')
 printed(name,'present' if path.is_file() else 'not found')

print('\n[ANALYSIS INTEGRATION IMPORTS]')
for description,(file,module) in INTEGRATIONS.items():
 path=SRC/file
 if not path.is_file():
  printed(description,'pipeline file missing')
 else:
  text=path.read_text(encoding='utf-8-sig')
  printed(description,'reference found' if module in text else 'NO REFERENCE (inspect alternate integration path)')

print('\n[FOCUSED TEST EVIDENCE — presence only]')
for segment in ('c6c1','c6c2','c6c3','c6c4','d2b','d3a','d3b','d3c'):
 found=sorted(x.name for x in TESTS.glob('test_dev077_gun_*.py') if segment in x.stem.lower())
 printed(segment,', '.join(found) if found else 'not found')

print('\n[FINAL AUDIT LIMITATIONS]')
print('  Static evidence cannot prove rule correctness, source-book parity or runtime test results.')
print('  Existing full regression and D2/D3 runtime evidence must accompany this audit.')
print('  No tournament-legality checks, source changes or CSV mutations performed.')
