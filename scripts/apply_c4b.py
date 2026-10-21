"""Conservative, idempotent local Fly registration and terrain movement adapter.

Preserves locally modified files; refuses unknown source shape. Backups created.
"""
from pathlib import Path
import csv
import shutil

ROOT = Path(__file__).resolve().parents[1]


def add_csv(relative, row, key):
    path = ROOT / relative
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    if not fields or not set(row) <= set(fields):
        raise ValueError(f"Unexpected CSV header: {relative}")
    matches = [r for r in rows if tuple(r[k] for k in key) == tuple(row[k] for k in key)]
    if matches:
        if len(matches) > 1 or any(any((r.get(k) or "") != (row.get(k) or "") for k in row) for r in matches):
            raise ValueError(f"Conflicting or duplicate registration: {relative}")
        print(f"Already present: {relative} {tuple(row[k] for k in key)}")
        return
    shutil.copy2(path, str(path) + ".c4b.bak")
    rows.append({f: row.get(f, "") for f in fields})
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"Updated {relative}")


add_csv("data/rules/special_rules.csv",
        {"id": "FLY", "name": "Fly", "category": "MOVEMENT"}, ("id",))
add_csv("data/profiles/profile_special_rules.csv",
        {"profile_id": "WAR_BAT", "rule_id": "FLY", "parameter": ""},
        ("profile_id", "rule_id"))

path = ROOT / "src/terrain_movement.py"
text = path.read_text(encoding="utf-8")
marker = "    movement = combatant.effective_movement\n"
replacement = '''    # Fly is an elected mode, not a permanent terrain exemption.
    # The optional keyword preserves all existing call sites.
    if flight_mode is not None:
        from flying_movement import FlightMode, flight_movement
        result = flight_movement(
            combatant, flight_mode,
            currently_in_woodland=currently_in_woodland,
        )
        if flight_mode is FlightMode.FLY:
            return result.distance_inches
        # Grounded Flyers have 4-inch movement and ordinary terrain rules.
        movement = result.distance_inches
    else:
        movement = combatant.effective_movement
'''
sig = '''    is_woodland: bool = False,
) -> float:
    """Movement inches for a declared terrain category; no terrain assumed."""'''
new_sig = '''    is_woodland: bool = False,
    flight_mode=None,
    currently_in_woodland: bool = False,
) -> float:
    """Movement inches for terrain, optionally with an explicit Fly mode."""'''
if new_sig in text and replacement in text:
    print("terrain_movement.py already patched")
elif text.count(sig) == 1 and text.count(marker) == 1:
    updated = text.replace(sig, new_sig, 1).replace(marker, replacement, 1)
    shutil.copy2(path, str(path) + ".c4b.bak")
    path.write_text(updated, encoding="utf-8")
    print("Updated src/terrain_movement.py")
else:
    raise ValueError("Unrecognised terrain_movement.py: stopped without patching it")
