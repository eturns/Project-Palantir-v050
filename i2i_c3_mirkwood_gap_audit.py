"""DEV-077S-I2-I-C3-D7-B4: read-only Mirkwood import readiness audit.

Run from repository root. No profile statistics, rule effects or weapons are invented.
This does not certify army legality or calculate a Shooting rating.
"""
import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

REQUIRED_MODELS = {
    '[rangers-of-mirkwood] legolas-greenleaf-prince-of-mirkwood': 'Legolas',
    '[rangers-of-mirkwood] tauriel-ranger-of-mirkwood': 'Tauriel',
    '[rangers-of-mirkwood] mirkwood-ranger-captain': 'Ranger Captain',
    '[rangers-of-mirkwood] mirkwood-ranger': 'Mirkwood Ranger',
}
REQUIRED_OPTIONS = ('OPT0771', 'OPT0772')


def csv_rows(paths):
    """Load CSV data without modifying global loader configuration."""
    result = []
    for path in paths:
        with path.open(encoding='utf-8-sig', newline='') as f:
            result.extend(csv.DictReader(f))
    return result


def analyze_export(data):
    if data.get('armyList') != 'Rangers of Mirkwood':
        raise ValueError('This audit requires a Rangers of Mirkwood roster')
    units = {}
    options = set()
    bow_limit_count = 0
    for band in data.get('warbands', []):
        hero = band.get('hero') or {}
        if hero.get('model_id'):
            mid = hero['model_id']
            units[mid] = units.get(mid, 0) + 1
            options.update(o['id'] for o in hero.get('options', []))
        for item in band.get('units', []):
            mid = item['model_id']
            count = item['quantity']
            if type(count) is not int or count <= 0:
                raise ValueError('Invalid model quantity')
            units[mid] = units.get(mid, 0) + count
            options.update(o['id'] for o in item.get('options', []))
        bow_limit_count += band.get('meta', {}).get('bows', 0)
    return units, options, bow_limit_count


def audit(root, roster):
    root, roster = Path(root), Path(roster)
    data = json.loads(roster.read_text(encoding='utf-8'))
    models, selected_options, bow_limit_count = analyze_export(data)
    from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS
    from importers.mesbg_list_builder_army_list_id_map import EXTERNAL_ARMY_LIST_IDS
    from loader import PROFILE_FILES

    blockers = []
    if 'Rangers of Mirkwood' not in EXTERNAL_ARMY_LIST_IDS:
        blockers.append('army_list_external_mapping_missing')
    profile_paths = [root / p for p in PROFILE_FILES]
    profile_rows = csv_rows(profile_paths)
    profile_ids = {r['id'] for r in profile_rows}
    mappings = {}
    for mid in models:
        pid = EXTERNAL_PROFILE_IDS.get(mid)
        mappings[mid] = pid
        if not pid:
            blockers.append('external_model_mapping_missing:' + mid)
        elif pid not in profile_ids:
            blockers.append('profile_not_loaded:' + pid)

    # Inspect actual option definitions, not exported display names.
    option_file = root / 'data/profiles/profile_options.csv'
    option_rows = csv_rows([option_file]) if option_file.exists() else []
    known_options = {r.get('external_id', '') for r in option_rows} | {
        r.get('id', '') for r in option_rows
    }
    for option in sorted(selected_options):
        if option not in known_options:
            blockers.append('option_definition_not_found:' + option)

    ranger_key = '[rangers-of-mirkwood] mirkwood-ranger'
    ranger_profile = mappings.get(ranger_key)
    ranger_row = next((r for r in profile_rows if r.get('id') == ranger_profile), None)
    default_file = root / 'data/profiles/profile_default_wargear.csv'
    default_rows = csv_rows([default_file]) if default_file.exists() else []
    ranger_default = [r for r in default_rows if ranger_profile and ranger_profile in r.values()]
    ranger_bow_ids = sorted({str(v) for row in ranger_default for v in row.values()
                            if 'BOW' in str(v).upper()})
    if not ranger_profile or not ranger_row or not ranger_bow_ids:
        blockers.append('ranger_default_bow_not_verified')

    # Metadata.bows is bow-limit accounting, never equipped-shooter evidence.
    return {
        'development': 'DEV-077S-I2-I-C3-D7-B4',
        'army': data.get('armyList'), 'model_count': sum(models.values()),
        'ranger_count': models.get(ranger_key, 0),
        'export_bow_limit_count': bow_limit_count,
        'export_bow_limit_count_is_equipped_bows': False,
        'external_models': models,
        'mapped_profiles': mappings,
        'selected_option_ids': sorted(selected_options),
        'ranger_default_bow_ids_found': ranger_bow_ids,
        'profile_data_ready': not blockers,
        'blockers': sorted(set(blockers)),
        'legality_verified': False,
        'shooting_validated': False,
        'calibration_eligible': False,
        'production_scoring_enabled': False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--roster', default='tests/fixtures/rangers-of-mirkwood.json')
    p.add_argument('--output', default=None)
    args = p.parse_args(argv)
    report = audit(ROOT, args.roster)
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open('x', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))
    # Readiness blockers are an expected audit finding, not a Python crash.
    return report


if __name__ == '__main__':
    main()
