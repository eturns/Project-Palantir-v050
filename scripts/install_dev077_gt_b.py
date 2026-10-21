"""DEV-077-GT-B: deterministic additive Goblin-town data installer.

Place in the repository scripts/ folder and run from the repository root with Python 3.14. Backs up touched files,
checks prerequisites and collisions, and never changes existing row definitions.
Does not add GT-C special rule mechanics.
"""
from __future__ import annotations

import csv
from io import StringIO
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent

PROFILES = '''id,name,points,movement,base_size_mm,fight,shooting,strength,defence,attacks,wounds,courage,intelligence,might,will,fate,max_in_army,heroic_status,model_types,races
GT_KING,The Goblin King,150,"6""",40,6,5+,5,5,3,3,6+,6+,3,2,1,1,HERO,INFANTRY|MONSTER|UNIQUE,GOBLIN
GT_GRINNAH,"Grinnah, Goblin Jailer",50,"5""",25,3,5+,4,4,2,2,7+,7+,2,1,1,1,HERO,INFANTRY|UNIQUE,GOBLIN
GT_SCRIBE,The Goblin Scribe,50,"0""",60,1,6+,2,2,1,1,7+,7+,0,1,1,1,HERO,INFANTRY|UNIQUE,GOBLIN
GT_CAPTAIN,Goblin Captain,40,"5""",25,3,5+,4,4,2,2,7+,7+,2,1,1,0,HERO,INFANTRY,GOBLIN
GT_GOLLUM,Gollum,40,"5""",25,4,4+,4,4,2,2,6+,5+,1,0,1,1,HERO,INFANTRY|UNIQUE,HOBBIT
GT_WARRIOR,Goblin Warrior,5,"5""",25,2,5+,3,3,1,1,8+,8+,0,0,0,0,WARRIOR,INFANTRY,GOBLIN
'''

# Profile rows are source-book stat lines; special rules are deferred to GT-C.
APPENDS = {
    'data/factions/factions.csv': '''id,name\nGOBLIN_TOWN,Goblin-town\n''',
    'data/factions/army_lists.csv': '''id,name,faction_id\nGOBLIN_TOWN,Goblin-town,GOBLIN_TOWN\n''',
    'data/factions/army_list_profiles.csv': '''army_list_id,profile_id\nGOBLIN_TOWN,GT_KING\nGOBLIN_TOWN,GT_GRINNAH\nGOBLIN_TOWN,GT_SCRIBE\nGOBLIN_TOWN,GT_CAPTAIN\nGOBLIN_TOWN,GT_GOLLUM\nGOBLIN_TOWN,GT_WARRIOR\n''',
    'data/profiles/profile_options.csv': '''id,profile_id,name,points,external_id,assigned_profile_ids,assigned_relationship_types,exclusive_group,required_group\nGT_WARRIOR_TWO_HANDED,GT_WARRIOR,Two-handed weapon,1,OPT0709,,,,\n''',
    'data/profiles/profile_option_wargear.csv': '''option_id,wargear_id,action\nGT_WARRIOR_TWO_HANDED,WG_TWO_HANDED_WEAPON,grant\n''',
    'data/profiles/profile_default_wargear.csv': '''profile_id,wargear_id\nGT_KING,WG_TWO_HANDED_WEAPON\nGT_GRINNAH,WG_HAND_WEAPON\nGT_CAPTAIN,WG_HAND_WEAPON\nGT_WARRIOR,WG_HAND_WEAPON\n''',
    'data/profiles/profile_heroic_actions.csv': '''profile_id,heroic_action_id\nGT_KING,HEROIC_CHALLENGE\nGT_KING,HEROIC_STRENGTH\nGT_KING,HEROIC_STRIKE\nGT_GRINNAH,HEROIC_CHALLENGE\nGT_CAPTAIN,HEROIC_MARCH\n''',
}

MAP_ENTRIES = {
    'src/importers/mesbg_list_builder_army_list_id_map.py': {"'Goblin-town'": "'GOBLIN_TOWN'"},
    'src/importers/mesbg_list_builder_profile_id_map.py': {
        "'[goblin-town] the-goblin-king'": "'GT_KING'",
        "'[goblin-town] grinnah-goblin-jailer'": "'GT_GRINNAH'",
        "'[goblin-town] the-goblin-scribe'": "'GT_SCRIBE'",
        "'[goblin-town] goblin-captain'": "'GT_CAPTAIN'",
        "'[goblin-town] gollum'": "'GT_GOLLUM'",
        "'[goblin-town] goblin-warrior'": "'GT_WARRIOR'",
    },
}


def parse_csv(text: str) -> tuple[list[str], list[dict[str, str]]]:
    reader = csv.DictReader(StringIO(text))
    return list(reader.fieldnames or []), list(reader)


def csv_text(fields: list[str], rows: list[dict[str, str]]) -> str:
    output = StringIO(newline='')
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def prepare_csv(path: Path, addition: str) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    existing_fields, rows = parse_csv(path.read_text(encoding='utf-8-sig'))
    new_fields, incoming = parse_csv(addition)
    if existing_fields != new_fields:
        raise ValueError(f'{path}: schema mismatch {existing_fields} != {new_fields}')
    # Accept exact pre-existing rows (idempotent), reject key collisions.
    keys = ('id', 'profile_id', 'army_list_id', 'option_id')
    key_fields = [k for k in keys if k in existing_fields]
    for add in incoming:
        if add in rows:
            continue
        # Compound identifiers for relationship tables permit repeated IDs.
        if 'id' in key_fields:
            collisions = [r for r in rows if r['id'] == add['id']]
            if collisions:
                raise ValueError(f'{path}: conflicting ID {add["id"]}')
        rows.append(add)
    return csv_text(existing_fields, rows)


def prepare_map(path: Path, additions: dict[str, str]) -> str:
    text = path.read_text(encoding='utf-8')
    if not text.rstrip().endswith('}'):
        raise ValueError(f'{path}: expected a final dictionary closing brace')
    insertions = []
    for key, val in additions.items():
        wanted = f'    {key}: {val},'
        if wanted in text:
            continue
        if key + ':' in text:
            raise ValueError(f'{path}: conflicting mapping for {key}')
        insertions.append(wanted)
    if not insertions:
        return text
    pos = text.rfind('}')
    return text[:pos] + '    # DEV-077-GT-B Goblin-town\n' + '\n'.join(insertions) + '\n' + text[pos:]


def prepare_loader(path: Path) -> str:
    text = path.read_text(encoding='utf-8')
    entry = '    "data/profiles/goblin_town_profiles.csv",'
    if entry in text:
        return text
    anchor = '    "data/profiles/gundabad_profiles.csv",'
    if anchor not in text:
        raise ValueError(f'{path}: expected Gundabad profile loader anchor absent')
    return text.replace(anchor, anchor + '\n' + entry, 1)


def main() -> None:
    missing = [p for p in [*APPENDS, *MAP_ENTRIES] if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit(f'Run from repository root. Missing: {missing}')
    targets: dict[Path, str] = {}
    for rel, data in APPENDS.items():
        path = ROOT / rel
        targets[path] = prepare_csv(path, data)
    for rel, entries in MAP_ENTRIES.items():
        path = ROOT / rel
        targets[path] = prepare_map(path, entries)
    loader_path = ROOT / 'src/loader.py'
    if not loader_path.is_file():
        raise FileNotFoundError(loader_path)
    targets[loader_path] = prepare_loader(loader_path)
    profile_path = ROOT / 'data/profiles/goblin_town_profiles.csv'
    if profile_path.exists() and profile_path.read_text(encoding='utf-8') != PROFILES:
        raise ValueError('Existing goblin_town_profiles.csv differs; refusing overwrite')
    targets[profile_path] = PROFILES
    for path, updated in targets.items():
        if path.exists():
            current = path.read_text(encoding='utf-8-sig')
            if current == updated:
                print('UNCHANGED', path.relative_to(ROOT))
                continue
            backup = path.with_name(path.name + '.gtb.bak')
            if not backup.exists():
                shutil.copy2(path, backup)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(updated, encoding='utf-8', newline='')
        print('UPDATED', path.relative_to(ROOT))


if __name__ == '__main__':
    main()
