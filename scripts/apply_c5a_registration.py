"""Idempotent Chittering Hordes registration; preserves previous local CSV edits."""
import csv
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def ensure(relative_path, row, identifying_fields):
    path = ROOT / relative_path
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or not set(row).issubset(fields):
        raise ValueError(f"Unexpected CSV schema in {relative_path}")
    matches = [existing for existing in rows if all(
        (existing.get(field) or "") == (row.get(field) or "")
        for field in identifying_fields
    )]
    if len(matches) > 1:
        raise ValueError(f"Duplicate registration in {relative_path}: {row}")
    if matches:
        if any((matches[0].get(field) or "") != value for field, value in row.items()):
            raise ValueError(f"Conflicting registration in {relative_path}: {row}")
        print(f"Already registered: {relative_path}: {row}")
        return
    shutil.copy2(path, path.with_suffix(path.suffix + ".c5a.bak"))
    rows.append({field: row.get(field, "") for field in fields})
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Registered: {relative_path}: {row}")


ensure(
    "data/rules/special_rules.csv",
    {"id": "CHITTERING_HORDES", "name": "Chittering Hordes", "category": "SPECIAL"},
    ("id",),
)
for profile_id in ("GOBLIN_MERCENARY", "GOBLIN_MERCENARY_CAPTAIN"):
    ensure(
        "data/profiles/profile_special_rules.csv",
        {"profile_id": profile_id, "rule_id": "CHITTERING_HORDES", "parameter": ""},
        ("profile_id", "rule_id"),
    )
