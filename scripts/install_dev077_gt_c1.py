"""DEV-077-GT-C1: additive, idempotent Goblin-town core rule registrations.

Run from the repository root: py -3.14 scripts/install_dev077_gt_c1.py
No changes to scoring, rule effect algorithms, or existing rows.
"""
from __future__ import annotations
import csv
from io import StringIO
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent

RULES = (
    ("CAVE_DWELLER", "Cave Dweller", "MOVEMENT"),
    ("MOUNTAIN_DWELLER", "Mountain Dweller", "MOVEMENT"),
    ("RESISTANT_TO_MAGIC", "Resistant to Magic", "MAGIC"),
)

ASSIGNMENTS = {
    "GT_KING": ("BURLY", "CAVE_DWELLER", "RESISTANT_TO_MAGIC", "TERROR", "RELENTLESS_ADVANCE"),
    "GT_GRINNAH": ("CAVE_DWELLER", "CHITTERING_HORDES"),
    "GT_SCRIBE": (),
    "GT_CAPTAIN": ("CAVE_DWELLER", "CHITTERING_HORDES"),
    "GT_GOLLUM": ("CAVE_DWELLER", "MOUNTAIN_DWELLER", "STALK_UNSEEN"),
    "GT_WARRIOR": ("CAVE_DWELLER", "CHITTERING_HORDES"),
}
# These are rule *registrations*, not claims of mechanical completeness.
# Goblin King's Relentless Advance uses a currently Ogre-specific resolver;
# do not mark Goblin King movement as mechanically implemented.

def read(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r=csv.DictReader(f)
        return tuple(r.fieldnames or ()),list(r)

def render(fields, rows):
    stream=StringIO(newline="")
    w=csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return stream.getvalue()

def prepare(path, expected_fields, additions, keys):
    if not path.is_file():
        raise FileNotFoundError(path)
    fields, rows=read(path)
    if fields != expected_fields:
        raise ValueError(f"Unexpected schema in {path}: {fields}")
    index = {}
    for existing in rows:
        key = tuple(existing[k] for k in keys)
        if key in index:
            raise ValueError(f"Duplicate existing key in {path}: {key}")
        index[key] = existing
    for incoming in additions:
        key=tuple(incoming[k] for k in keys)
        if key in index:
            if index[key] != incoming:
                raise ValueError(f"Conflicting existing row in {path}: {key}")
            continue
        rows.append(incoming)
        index[key]=incoming
    return render(fields,rows)

def main():
    profile_path=ROOT/"data/profiles/goblin_town_profiles.csv"
    fields, profiles=read(profile_path)
    actual={p["id"] for p in profiles}
    if not set(ASSIGNMENTS).issubset(actual):
        raise RuntimeError("GT-B profiles missing; C1 installation halted")
    rules_path=ROOT/"data/rules/special_rules.csv"
    assignments_path=ROOT/"data/profiles/profile_special_rules.csv"
    rules_fields, existing_rules=read(rules_path)
    available={r["id"] for r in existing_rules}|{r[0] for r in RULES}
    referenced={rule for items in ASSIGNMENTS.values() for rule in items}
    if not referenced.issubset(available):
        raise RuntimeError(f"Missing prerequisite core rule: {sorted(referenced-available)}")
    rule_updates=prepare(
        rules_path,("id","name","category"),
        [{"id":i,"name":n,"category":c} for i,n,c in RULES],("id",))
    assignment_updates=prepare(
        assignments_path,("profile_id","rule_id","parameter"),
        [{"profile_id":profile,"rule_id":rule,"parameter":""}
         for profile, rules in ASSIGNMENTS.items() for rule in rules],
        ("profile_id","rule_id","parameter"))
    updates={rules_path:rule_updates,assignments_path:assignment_updates}
    # Validate both files in memory before writing either.
    for path, content in updates.items():
        original=path.read_text(encoding="utf-8-sig")
        if original==content:
            print("UNCHANGED",path.relative_to(ROOT))
            continue
        backup=path.with_name(path.name+".gtc1.bak")
        if not backup.exists():
            shutil.copy2(path,backup)
        path.write_text(content,encoding="utf-8",newline="")
        print("UPDATED",path.relative_to(ROOT))
    print("GT-C1 rule registrations complete; conditional mechanics deferred.")

if __name__=="__main__":
    main()
