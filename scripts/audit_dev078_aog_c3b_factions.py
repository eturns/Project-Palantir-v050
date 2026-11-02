"""Project Palantir — DEV-078-AoG-C3-B, controlled faction classification.
Author: Edward Turns (Project Lead)

Run from repository root. Defaults to read-only; --apply writes only guarded,
explicit assignments and preserves all previous data/columns.
"""
from __future__ import annotations
import argparse
import csv
import io
from pathlib import Path

FILES = ('dol_guldur','iron_hills','lake_town','gundabad','goblin_town',
         'three_trolls','smaug','erebor','dale','beornings','mirkwood')
# Every entry is deliberate. This is NOT a file-based or race-based guess.
# A model may belong to a different faction from its source CSV file.
GROUPS = {
    'IRON_HILLS': ('IH_WR','IH_DAIN','IH_CAP','IH_GR','IH_CHARIOT','IH_SIEGE_CREW'),
    'EREBOR': ('BOFUR_CHAMPION_OF_EREBOR',),
    'DALE': ('DALE_GIRION','DALE_CAPTAIN','DALE_WARRIOR','DALE_SIEGE_CREW'),
    'LAKE_TOWN': ('BAIN','SIGRID','TILDA','BARD','LAKE_TOWN_MILITIA'),
    'MIRKWOOD': ('MW_LEGOLAS','MW_TAURIEL','MW_RANGER_CAPTAIN','MW_RANGER'),
    'GOBLIN_TOWN': ('GT_KING','GT_GRINNAH','GT_SCRIBE','GT_CAPTAIN','GT_WARRIOR'),
    'GUNDABAD': ('AZOG_THE_DEFILER','BOLG_SPAWN_OF_AZOG',
                 'GUNDABAD_CATAPULT_TROLL','ORC_COMMANDER','TROLL_BRUTE',
                 'GUNDABAD_ORC_CAPTAIN','GUNDABAD_ORC_WARRIOR',
                 'GUNDABAD_BERSERKER','GUNDABAD_OGRE','GUNDABAD_TROLL',
                 'WAR_BAT','GOBLIN_MERCENARY_CAPTAIN','GOBLIN_MERCENARY',
                 'WHITE_WARG_SEPARATED'),
    'DG': ('DG_NEC','DG_WK','DG_KHM','DG_DH','DG_FS','DG_LS','DG_AK',
           'DG_SM','DG_MGS','DG_MHS','DG_KEEPER','DG_CASTELLAN'),
}
REVIEW = {
    'THRAIN_THE_BROKEN':'Captive/altered state; confirm official faction keyword',
    'GT_GOLLUM':'Independent model included in Goblin-town army; review canonical affiliation',
    'TT_BILL':'Three Trolls faction coding not established',
    'TT_BERT':'Three Trolls faction coding not established',
    'TT_TOM':'Three Trolls faction coding not established',
    'SMAUG':'Do not infer Erebor from place name; confirm proper faction',
    'BEORN':'Confirm Beornings faction keyword',
    'BEORN_THE_BEAR':'Confirm transformed model affiliation',
    'DG_HOC':'Hunter Orc appears in multiple lists; verify model faction',
    'DG_HOW':'Hunter Orc appears in multiple lists; verify model faction',
    'DG_HOWR':'Hunter Orc appears in multiple lists; verify model faction',
    'DG_FW':'Warg appears in multiple lists; verify model faction',
    'YAZNEG':'Confirm hunter faction identity',
    'NARZUG':'Confirm hunter faction identity',
    'FIMBUL':'Confirm hunter faction identity',
}
ASSIGNMENTS = {pid:faction for faction, ids in GROUPS.items() for pid in ids}
assert len(ASSIGNMENTS)==sum(len(ids) for ids in GROUPS.values()), 'duplicate assigned profile'
assert not (set(ASSIGNMENTS)&set(REVIEW)), 'review and assignment overlap'


def run(root:Path, *, apply:bool=False):
    changes=[]; report=[]; seen=set(); pending=[]
    for name in FILES:
        path=root/'data'/'profiles'/f'{name}_profiles.csv'
        with path.open('r',encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            fields=reader.fieldnames
            if fields is None: raise ValueError(f'Empty profile CSV: {path}')
            rows=list(reader)
        if 'id' not in fields or 'races' not in fields: raise ValueError(f'Missing required columns: {path}')
        if any(None in row for row in rows): raise ValueError(f'Invalid CSV columns: {path}')
        for row in rows:
            pid=row['id']
            if pid in seen: raise ValueError(f'Duplicate profile ID: {pid}')
            seen.add(pid)
            desired=ASSIGNMENTS.get(pid)
            current=(row.get('factions') or '').strip()
            if desired:
                if current and current!=desired:
                    raise ValueError(f'Conflicting affiliation {pid}: existing={current}, proposal={desired}; manual review required')
                status='confirmed_assignment'
            else:
                status='review_required' if not current else 'existing_unreviewed'
                pending.append(pid)
            report.append({'profile_id':pid,'file':path.name,'race':row['races'],
                           'existing_factions':current,'proposed_factions':desired or '',
                           'status':status,'notes':REVIEW.get(pid,'Verify canonical model faction; do not infer from roster') if not desired else ''})
            if apply and desired and not current:
                row['factions']=desired
        if apply:
            new_fields=list(fields)
            if 'factions' not in new_fields: new_fields.append('factions')
            buf=io.StringIO(newline='')
            writer=csv.DictWriter(buf, fieldnames=new_fields,lineterminator='\n')
            writer.writeheader();writer.writerows(rows)
            changes.append((path,buf.getvalue()))
    unknown=set(ASSIGNMENTS)-seen
    if unknown:raise ValueError(f'Unknown profile IDs in classification mapping: {sorted(unknown)}')
    # Validate ALL files and assignments before writing ANY file.
    if apply:
        for path, content in changes: path.write_text(content,encoding='utf-8',newline='')
    report_path=root/'dev078_aog_c3b_faction_report.csv'
    with report_path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report[0]));writer.writeheader();writer.writerows(report)
    print(f'Profiles: {len(report)} | assigned: {len(ASSIGNMENTS)} | review: {len(pending)} | mode: {"APPLY" if apply else "READ-ONLY"}')
    print(f'Report: {report_path}')
    for pid in pending:print(f'  REVIEW: {pid} — {REVIEW.get(pid,"Verify canonical affiliation")}')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    run(Path.cwd(),apply=args.apply)
