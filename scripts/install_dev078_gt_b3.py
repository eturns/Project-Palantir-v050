"""DEV-078-GT-B3 idempotent production service wiring.

Author: Edward Turns (Project Lead).
Run from project root: py -3.14 scripts/install_dev078_gt_b3.py
Only inserts guarded optional diagnostics; preserves existing Gundabad code.
"""
from pathlib import Path

path = Path("src/services/army_analysis_service.py")
text = path.read_text(encoding="utf-8")
marker = "from goblin_town_songs_service import build_goblin_town_song_army_evidence"
if marker in text:
    print("GT-B3 already installed; no changes")
    raise SystemExit(0)

def once(old, new):
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one service anchor, found {count}: {old[:85]}")
    text = text.replace(old, new, 1)

once("from gundabad_raise_the_banners_service import build_raise_the_banners_army_evidence",
     "from gundabad_raise_the_banners_service import build_raise_the_banners_army_evidence\n"
     + marker)
once("    gundabad_banner_request=None,\n) -> dict:",
     "    gundabad_banner_request=None,\n    goblin_town_army_definition=None,\n    goblin_town_song_request=None,\n) -> dict:")
once("    mechanical_raise_the_banners = None\n",
     "    mechanical_raise_the_banners = None\n    mechanical_goblin_town_songs = None\n")
once("            if gundabad_banner_request is not None:\n",
     "            if goblin_town_song_request is not None:\n"
     "                if goblin_town_army_definition is None:\n"
     "                    raise ValueError('Song request requires imported Goblin-town definition')\n"
     "                mechanical_goblin_town_songs = build_goblin_town_song_army_evidence(\n"
     "                    army, army_list, army_definition=goblin_town_army_definition,\n"
     "                    request=goblin_town_song_request,\n"
     "                )\n"
     "            if gundabad_banner_request is not None:\n")
once("              or gundabad_banner_request is not None):",
     "              or gundabad_banner_request is not None\n"
     "              or goblin_town_song_request is not None\n"
     "              or goblin_town_army_definition is not None):")
once("        gundabad_banner_request,\n    )):",
     "        gundabad_banner_request,\n"
     "        goblin_town_song_request,\n"
     "        goblin_town_army_definition,\n    )):")
once("    if mechanical_raise_the_banners is not None:\n",
     "    if mechanical_goblin_town_songs is not None:\n"
     "        result['mechanical_goblin_town_songs'] = mechanical_goblin_town_songs\n"
     "    if mechanical_raise_the_banners is not None:\n")
compile(text, str(path), "exec")
path.write_text(text, encoding="utf-8")
print("GT-B3 service integration installed (syntax checked)")
