"""DEV-077-GT-C3B1: register Goblin Scribe's IMMOBILE special rule.

Idempotent for existing identical registrations; fails on conflicting values.
Does not remove historical CSV rows or change dashboard scoring.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def insert_if_missing(path: Path, entry: dict, keys: tuple[str, ...]):
    with path.open(encoding="utf-8-sig",newline="") as fh:
        reader=csv.DictReader(fh)
        cols=reader.fieldnames
        rows=list(reader)
    if set(cols or ()) != set(entry):
        raise ValueError(f"Unexpected CSV columns for {path.name}: {cols}")
    matches=[row for row in rows if all(row[key]==entry[key] for key in keys)]
    if matches:
        if len(matches)>1 or matches[0]!=entry:
            raise ValueError(f"Conflicting/duplicate registration in {path}")
        print("Already present:",path.name,entry)
        return
    with path.open("a",encoding="utf-8",newline="") as fh:
        writer=csv.DictWriter(fh,fieldnames=cols)
        writer.writerow(entry)
    print("Registered:",path.name,entry)


def main():
    insert_if_missing(ROOT/"data/rules/special_rules.csv",
        {"id":"IMMOBILE","name":"Immobile","category":"MOVEMENT"},("id",))
    insert_if_missing(ROOT/"data/profiles/profile_special_rules.csv",
        {"profile_id":"GT_SCRIBE","rule_id":"IMMOBILE","parameter":""},
        ("profile_id","rule_id","parameter"))


if __name__ == "__main__":
    main()
