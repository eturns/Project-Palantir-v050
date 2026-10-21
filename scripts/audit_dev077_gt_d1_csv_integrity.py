"""Read-only CSV integrity audit: no edits and no guessed relationships."""
import csv
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
KEYS={
    'special_rules.csv':('id',),
    'profile_special_rules.csv':('profile_id','rule_id','parameter'),
    'profile_options.csv':('id',),
    'wargear.csv':('id',),
    'army_lists.csv':('id',),
    'goblin_town_profiles.csv':('id',),
}

def audit(root=ROOT):
    issues=[]
    count=0
    paths=sorted((root/'data').rglob('*.csv'))
    for path in paths:
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            cols=tuple(reader.fieldnames or ())
            rows=list(reader)
        count+=len(rows)
        label=str(path.relative_to(root))
        if not cols or len(cols)!=len(set(cols)):
            issues.append(f'{label}: missing or duplicate headers')
            continue
        key=KEYS.get(path.name)
        seen={}
        for line,row in enumerate(rows,2):
            if None in row or any(v is None for v in row.values()):
                issues.append(f'{label}:{line}: malformed row')
            if key and all(k in cols for k in key):
                identity=tuple(row[k] for k in key)
                if identity in seen:
                    issues.append(f'{label}:{line}: duplicate {identity}, first at {seen[identity]}')
                seen[identity]=line
    print(f'READ ONLY: {len(paths)} CSVs; {count} data rows; {len(issues)} issues')
    for issue in issues: print('ISSUE',issue)
    return issues

if __name__=='__main__':
    raise SystemExit(bool(audit()))
