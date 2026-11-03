"""DEV-078-GT-C2 guarded, idempotent installer.
Author: Edward Turns (Project Lead).
Run from repository root; preserves existing GT-B3 and Gundabad logic.
"""
from pathlib import Path

service = Path("src/services/army_analysis_service.py")
rules = Path("data/factions/army_rules.csv")
s = service.read_text(encoding="utf-8")
csv = rules.read_text(encoding="utf-8-sig")
imp = "from goblin_town_strength_in_numbers_service import build_strength_in_numbers_army_evidence"
row = "GOBLIN_TOWN,GT_STRENGTH_IN_NUMBERS,Strength in Numbers"
if imp in s:
    if row not in csv.splitlines():
        raise RuntimeError("Service wired but CSV registration missing")
    print("GT-C2 already installed")
    raise SystemExit(0)

def replace_once(old, new):
    global s
    n=s.count(old)
    if n != 1:
        raise RuntimeError(f"GT-C2 anchor expected once, found {n}: {old[:70]}")
    s=s.replace(old,new,1)

replace_once(
    "from goblin_town_songs_service import build_goblin_town_song_army_evidence",
    "from goblin_town_songs_service import build_goblin_town_song_army_evidence\n"+imp)
replace_once(
    "    goblin_town_song_request=None,\n) -> dict:",
    "    goblin_town_song_request=None,\n    goblin_town_strength_request=None,\n) -> dict:")
replace_once(
    "    mechanical_goblin_town_songs = None\n",
    "    mechanical_goblin_town_songs = None\n    mechanical_strength_in_numbers = None\n")
replace_once(
    "            if goblin_town_song_request is not None:\n",
    "            if goblin_town_strength_request is not None:\n"
    "                mechanical_strength_in_numbers = build_strength_in_numbers_army_evidence(\n"
    "                    army, army_list, request=goblin_town_strength_request,\n"
    "                )\n"
    "            if goblin_town_song_request is not None:\n")
replace_once(
    "              or goblin_town_army_definition is not None):",
    "              or goblin_town_army_definition is not None\n"
    "              or goblin_town_strength_request is not None):")
replace_once(
    "        goblin_town_army_definition,\n    )):",
    "        goblin_town_army_definition,\n"
    "        goblin_town_strength_request,\n    )):")
replace_once(
    "    if mechanical_goblin_town_songs is not None:\n",
    "    if mechanical_strength_in_numbers is not None:\n"
    "        result['mechanical_strength_in_numbers'] = mechanical_strength_in_numbers\n"
    "    if mechanical_goblin_town_songs is not None:\n")
compile(s,str(service),"exec")
if row not in csv.splitlines():
    csv=csv.rstrip("\r\n")+"\n"+row+"\n"
# Both files checked before either write.
service.write_text(s,encoding="utf-8")
rules.write_text(csv,encoding="utf-8")
print("GT-C2 service and rule registration installed (syntax checked)")
