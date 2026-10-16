"""B5: read-only real roster shooting measurement, no scoring changes."""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path

from importers.mesbg_list_builder_json_importer import import_army_definition_from_json
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from loader import load_all_profiles
from army_loader import load_army_list_profiles, load_army_lists, load_factions
from profile_option_loader import build_profile_options_by_external_id, load_profile_options
from mount_loader import load_mounts
from profile_option_mount_loader import load_profile_option_mount_assignments
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from ranged_weapon_resolver import resolve_ranged_weapon
from shooting_attack_count import get_effective_shooting_attack_count
from army_shooting_capability import resolve_army_ranged_shooters

FIXTURE = Path("tests/fixtures/rangers-of-mirkwood.json")
EXPECTED = {"MW_LEGOLAS": 1, "MW_TAURIEL": 1, "MW_RANGER_CAPTAIN": 1, "MW_RANGER": 30}


def load_reference_army(path=FIXTURE):
    if not Path(path).is_file():
        raise FileNotFoundError(path)
    profiles = {p.id:p for p in load_all_profiles()}
    opts = load_profile_options(profiles=profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles,wargear=wargear)
    load_profile_option_mount_assignments(profile_options=opts,mounts=load_mounts())
    load_profile_option_wargear_assignments(profile_options=opts,wargear=wargear)
    load_profile_special_rules(profiles=profiles,special_rules=load_special_rules())
    armies = load_army_lists(load_factions())
    load_army_list_profiles(army_lists=armies,profiles_by_id=profiles)
    _, army, _ = import_army_from_mesbg_list_builder(
        str(path), profiles_by_id=profiles, army_lists_by_id=armies,
        profile_options_by_external_id=build_profile_options_by_external_id(opts))
    return army


def measure(path=FIXTURE):
    definition=import_army_definition_from_json(str(path))
    army=load_reference_army(path)
    models=tuple(army.fielded_models())
    roster=Counter(m.configured_profile.profile.id for m in models)
    shooters=resolve_army_ranged_shooters(army)
    by_profile=Counter()
    attacks_by_profile=Counter()
    unknown=[]
    for configured, weapon in shooters:
        pid=configured.profile.id
        by_profile[pid]+=1
        if weapon.wargear_id!="WG_ELF_BOW" or not weapon.is_mechanically_complete:
            unknown.append({"profile":pid,"weapon":weapon.wargear_id})
        attacks_by_profile[pid]+=weapon.shots*get_effective_shooting_attack_count(configured)
    issues=[]
    if definition.army_list_id!="RANGERS_OF_MIRKWOOD": issues.append("wrong_army_list")
    if army.total_points()!=700: issues.append("not_700_points")
    if len(models)!=33: issues.append("not_33_models")
    if dict(roster)!=EXPECTED: issues.append("roster_composition_mismatch")
    if len(shooters)!=len(models): issues.append("missing_shooters")
    if unknown: issues.append("unrecognised_or_incomplete_bow")
    if dict(by_profile)!=EXPECTED: issues.append("bow_profile_distribution_mismatch")
    if sum(attacks_by_profile.values())!=36: issues.append("shooting_attack_total_mismatch")
    return {
        "stage":"B5","army_list":definition.army_list_id,
        "points":army.total_points(),"models":len(models),
        "composition":dict(sorted(roster.items())),
        "recognised_bows":len(shooters),
        "bow_model_counts":dict(sorted(by_profile.items())),
        "normal_shooting_attacks":sum(attacks_by_profile.values()),
        "attacks_by_profile":dict(sorted(attacks_by_profile.items())),
        "unexpected_weapon_records":unknown,"blockers":issues,
        "measurement_qualified":not issues,
        "battlefield_assumptions":"No movement, target, line of sight or in-the-way state inferred",
        "calibration_anchors_approved":False,"production_scoring_modified":False,
    }


if __name__=="__main__":
    print(json.dumps(measure(),indent=2))
