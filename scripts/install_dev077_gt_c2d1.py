"""DEV-077-GT-C2D1: idempotent rule registration for Blubbery Mass."""
from pathlib import Path
import csv
import io

ROOT=Path(__file__).resolve().parents[1]


def stage(path, new_row, key_cols):
    with path.open(encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f)
        fields=tuple(reader.fieldnames or ())
        rows=list(reader)
    if set(new_row) != set(fields):
        raise ValueError(f"Unexpected columns: {fields}")
    key=tuple(new_row[c] for c in key_cols)
    found=[r for r in rows if tuple(r[c] for c in key_cols)==key]
    if found:
        if len(found)!=1 or found[0]!=new_row:
            raise ValueError(f"Conflicting or duplicate registration: {key}")
        return None
    buffer=io.StringIO()
    writer=csv.DictWriter(buffer,fieldnames=fields,lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows+[new_row])
    return buffer.getvalue()


def main():
    rules=ROOT/"data/rules/special_rules.csv"
    relations=ROOT/"data/profiles/profile_special_rules.csv"
    if not (ROOT/"data/profiles/goblin_town_profiles.csv").exists():
        raise FileNotFoundError("Goblin-town GT-B profiles missing")
    changes=(
        (rules,stage(rules,{"id":"BLUBBERY_MASS","name":"Blubbery Mass",
                            "category":"DEFENCE"},("id",))),
        (relations,stage(relations,{"profile_id":"GT_KING",
                                   "rule_id":"BLUBBERY_MASS","parameter":""},
                         ("profile_id","rule_id","parameter"))),
    )
    for path,content in changes:
        if content is not None:
            path.write_text(content,encoding="utf-8",newline="")
            print("REGISTERED",path.relative_to(ROOT))
        else:
            print("ALREADY REGISTERED",path.relative_to(ROOT))


if __name__=="__main__":
    main()
