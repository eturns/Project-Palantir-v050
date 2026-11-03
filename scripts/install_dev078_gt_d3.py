"""DEV-078-GT-D3: guarded, repeat-safe prisoner service integration.

Author: Edward Turns (Project Lead).
Run from repository root: py -3.14 scripts/install_dev078_gt_d3.py
Existing GT-B3, GT-C2 and Gundabad integrations remain unchanged.
"""
from pathlib import Path

service = Path('src/services/army_analysis_service.py')
rules = Path('data/factions/army_rules.csv')
s = service.read_text(encoding='utf-8')
csv = rules.read_text(encoding='utf-8-sig')
import_line = 'from goblin_town_prisoner_service import build_goblin_town_prisoner_army_evidence'
rule_row = 'GOBLIN_TOWN,GT_IF_THEY_WONT_TALK,"If They Won\'t Talk, We\'ll Make Them Squawk!"'
if import_line in s:
    if rule_row not in csv.splitlines():
        raise RuntimeError('Prisoner service installed but missing army-rule registration')
    print('GT-D3 already installed')
    raise SystemExit(0)


def replace_once(old, new):
    global s
    found = s.count(old)
    if found != 1:
        raise RuntimeError(f'GT-D3 expected exactly one service anchor, found {found}: {old[:90]}')
    s = s.replace(old, new, 1)


replace_once(
    'from goblin_town_strength_in_numbers_service import build_strength_in_numbers_army_evidence',
    'from goblin_town_strength_in_numbers_service import build_strength_in_numbers_army_evidence\n' + import_line,
)
replace_once(
    '    goblin_town_strength_request=None,\n) -> dict:',
    '    goblin_town_strength_request=None,\n    goblin_town_prisoner_request=None,\n) -> dict:',
)
replace_once(
    '    mechanical_strength_in_numbers = None\n',
    '    mechanical_strength_in_numbers = None\n    mechanical_goblin_town_prisoners = None\n',
)
replace_once(
    '            if goblin_town_strength_request is not None:\n',
    '            if goblin_town_prisoner_request is not None:\n'
    '                mechanical_goblin_town_prisoners = build_goblin_town_prisoner_army_evidence(\n'
    '                    army, army_list, request=goblin_town_prisoner_request,\n'
    '                )\n'
    '            if goblin_town_strength_request is not None:\n',
)
replace_once(
    '              or goblin_town_strength_request is not None):',
    '              or goblin_town_strength_request is not None\n'
    '              or goblin_town_prisoner_request is not None):',
)
replace_once(
    '        goblin_town_strength_request,\n    )):',
    '        goblin_town_strength_request,\n'
    '        goblin_town_prisoner_request,\n    )):',
)
replace_once(
    '    if mechanical_strength_in_numbers is not None:\n',
    '    if mechanical_goblin_town_prisoners is not None:\n'
    "        result['mechanical_goblin_town_prisoners'] = mechanical_goblin_town_prisoners\n"
    '    if mechanical_strength_in_numbers is not None:\n',
)
compile(s, str(service), 'exec')
if rule_row not in csv.splitlines():
    csv = csv.rstrip('\r\n') + '\n' + rule_row + '\n'
# Validate both before writing either file.
service.write_text(s, encoding='utf-8')
rules.write_text(csv, encoding='utf-8')
print('GT-D3 service and prisoner army rule installed (syntax checked)')
