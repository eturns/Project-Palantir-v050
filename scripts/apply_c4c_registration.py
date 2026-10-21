"""Preserve current local C2-C4 data; add only the Pluck catalogue/assignment rows."""
import csv
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def ensure_row(relative_path, row, key_columns):
    path = ROOT / relative_path
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    if fields is None or not set(row).issubset(fields):
        raise ValueError(f"Unexpected CSV fields: {path}")
    key = tuple(row[field] for field in key_columns)
    matches = [r for r in rows if tuple(r[field] for field in key_columns) == key]
    if matches:
        if len(matches) != 1 or any(
            (matches[0].get(field) or "") != (value or "")
            for field, value in row.items()
        ):
            raise ValueError(f"Conflicting existing registration: {path}: {key}")
        print(f"Already registered: {key}")
        return
    shutil.copy2(path, path.with_suffix(path.suffix + ".c4c.bak"))
    rows.append({field: row.get(field, "") for field in fields})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Registered {key}")


if __name__ == "__main__":
    ensure_row("data/rules/special_rules.csv",
               {"id": "PLUCK", "name": "Pluck", "category": "MOVEMENT"},
               ("id",))
    ensure_row("data/profiles/profile_special_rules.csv",
               {"profile_id": "WAR_BAT", "rule_id": "PLUCK", "parameter": ""},
               ("profile_id", "rule_id"))
