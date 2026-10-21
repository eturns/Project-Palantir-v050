"""Patch C2D4 army analysis service by adding C3 character evidence.

Refuses incompatible versions; only modifies known insertion anchors.
Creates a .gt_c3d_backup copy of the original.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
path=ROOT/"src/services/army_analysis_service.py"
s=path.read_text(encoding="utf-8")
if "goblin_town_character_evidence import build_goblin_town_character_evidence" in s:
    print("C3D already installed")
    raise SystemExit(0)
def insert(old,new):
    global s
    if s.count(old)!=1:
        raise RuntimeError(f"Unexpected service structure; anchor not unique: {old!r}")
    s=s.replace(old,new,1)
insert("from goblin_king_mechanical_evidence import build_goblin_king_mechanical_evidence",
       "from goblin_king_mechanical_evidence import build_goblin_king_mechanical_evidence\n"
       "from goblin_town_character_evidence import build_goblin_town_character_evidence")
insert("    goblin_king_charge_contexts_by_king_id=None,\n",
       "    goblin_king_charge_contexts_by_king_id=None,\n"
       "    grinnah_swap_contexts_by_model_id=None,\n"
       "    goblin_scribe_contexts_by_model_id=None,\n"
       "    gollum_contexts_by_model_id=None,\n")
insert("    mechanical_goblin_king = None\n",
       "    mechanical_goblin_king = None\n"
       "    mechanical_goblin_town_characters = None\n")
insert("        mechanical_goblin_king = build_goblin_king_mechanical_evidence(\n",
       "        mechanical_goblin_town_characters = build_goblin_town_character_evidence(\n"
       "            army, grinnah_contexts=grinnah_swap_contexts_by_model_id,\n"
       "            scribe_contexts=goblin_scribe_contexts_by_model_id,\n"
       "            gollum_contexts=gollum_contexts_by_model_id,\n"
       "        )\n"
       "        mechanical_goblin_king = build_goblin_king_mechanical_evidence(\n")
insert("    elif any(x is not None for x in (\n",
       "    elif any(x is not None for x in (\n"
       "        grinnah_swap_contexts_by_model_id,\n"
       "        goblin_scribe_contexts_by_model_id,\n"
       "        gollum_contexts_by_model_id,\n")
insert("    return result\n",
       "    if mechanical_goblin_town_characters is not None:\n"
       "        result['mechanical_goblin_town_characters'] = mechanical_goblin_town_characters\n"
       "    return result\n")
compile(s,str(path),"exec")
backup=path.with_suffix(".py.gt_c3d_backup")
if backup.exists():
    raise FileExistsError(f"Backup already exists: {backup}")
backup.write_text(path.read_text(encoding="utf-8"),encoding="utf-8")
path.write_text(s,encoding="utf-8")
print("Patched",path,"Backup:",backup)
