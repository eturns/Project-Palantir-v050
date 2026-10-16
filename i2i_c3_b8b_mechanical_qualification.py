"""B8-B read-only six-army option and ranged equipment qualification.

Verifies selected external options in actual configured profiles and targeted
physical effects. Unavailable equipment or platform is reported as a blocker,
never silently passed. A clean result does not approve all special rules.
"""
import json
from collections import Counter
from pathlib import Path

from i2i_c3_b8a_cohort_intake import FIXTURES, FIXTURE_DIR
from loader import load_all_profiles
from army_loader import load_factions, load_army_lists, load_army_list_profiles
from profile_option_loader import load_profile_options, build_profile_options_by_external_id
from mount_loader import load_mounts
from profile_option_mount_loader import load_profile_option_mount_assignments
from wargear_loader import load_wargear
from profile_default_wargear_loader import load_profile_default_wargear
from profile_option_wargear_loader import load_profile_option_wargear_assignments
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from model_platform_loader import load_platforms
from profile_option_platform_loader import load_profile_option_platform_assignments
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS
from ranged_weapon_resolver import resolve_ranged_weapon

# Purposeful focused expectations for the critical new reference selections.
CRITICAL_EFFECTS = {
    "OPT0777": ("mount", "MOUNT_WAR_BOAR"),
    "OPT0783": ("wargear", "WG_CROSSBOW"),
    "OPT0782": ("wargear", "WG_SHIELD"),
    "OPT0795": ("wargear", "WG_ARMOUR"),
    "OPT0798": ("wargear", "WG_SPEAR"),
    "OPT0719": ("platform", None),  # Actual platform must exist.
    "OPT0724": ("wargear", "WG_CROSSBOW"),
    "OPT0772": ("wargear", "WG_ELF_BOW"),
}


def load_reference_army_with_platforms(path):
    """Import a roster with full option mount, wargear and platform linkage.

    The earlier Mirkwood-only evidence loader did not require platforms;
    B8-B needs them to validate the Iron Hills Chariot.
    """
    profiles = {p.id: p for p in load_all_profiles()}
    options = load_profile_options(profiles=profiles)
    wargear = load_wargear()
    load_profile_default_wargear(profiles=profiles, wargear=wargear)
    load_profile_option_wargear_assignments(profile_options=options, wargear=wargear)
    load_profile_option_mount_assignments(profile_options=options, mounts=load_mounts())
    load_profile_option_platform_assignments(
        profile_options=options, platforms=load_platforms(),
    )
    load_profile_special_rules(profiles=profiles, special_rules=load_special_rules())
    armies = load_army_lists(load_factions())
    load_army_list_profiles(army_lists=armies, profiles_by_id=profiles)
    _, army, _ = import_army_from_mesbg_list_builder(
        str(path), profiles_by_id=profiles, army_lists_by_id=armies,
        profile_options_by_external_id=build_profile_options_by_external_id(options),
    )
    return army


def expected_option_counts(document):
    expected = Counter()
    for band in document["warbands"]:
        for raw in [band["hero"], *band.get("units", [])]:
            ext = raw["model_id"]
            canonical = EXTERNAL_PROFILE_IDS.get(ext)
            if canonical is None:
                raise ValueError(f"Unknown external model: {ext}")
            quantity = raw.get("quantity", 1)
            for option in raw.get("options", []):
                expected[(canonical, option["id"])] += quantity
    return expected


def evaluate_one(key, filename, *, root=FIXTURE_DIR, importer=load_reference_army_with_platforms):
    path = Path(root) / filename
    result = {"army": key, "status": "blocked", "issues": [], "option_checks": [],
              "resolved_shooters": 0, "ranged_wargear_without_profile": []}
    if not path.exists():
        result["issues"].append("missing_fixture")
        return result
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
        expected = expected_option_counts(document)
        army = importer(path)
        models = tuple(x.configured_profile for x in army.fielded_models()
                       if x.configured_profile is not None)
        selected = Counter((x.profile.id, o.external_id) for x in models
                           for o in x.selected_options)
        for (model_id, opt_id), quantity in sorted(expected.items()):
            actual = selected[(model_id, opt_id)]
            check = {"profile": model_id, "external_option": opt_id,
                     "expected_models": quantity, "selected_models": actual}
            if actual != quantity:
                result["issues"].append(f"option_quantity_mismatch:{model_id}:{opt_id}")
            effect = CRITICAL_EFFECTS.get(opt_id)
            if effect is not None:
                kind, target = effect
                chosen = [x for x in models if x.profile.id == model_id
                          and any(o.external_id == opt_id for o in x.selected_options)]
                def correct(x):
                    if kind == "mount":
                        return x.effective_mount is not None and x.effective_mount.id == target
                    if kind == "platform":
                        return x.effective_platform is not None
                    return target in {w.id for w in x.effective_wargear}
                passing = sum(correct(x) for x in chosen)
                check["effect"] = kind
                check["effect_confirmed_models"] = passing
                if passing != quantity:
                    result["issues"].append(f"effect_not_applied:{model_id}:{opt_id}")
            result["option_checks"].append(check)
        for model in models:
            weapon = resolve_ranged_weapon(model)
            if weapon is not None:
                result["resolved_shooters"] += 1
                if not weapon.is_mechanically_complete:
                    result["issues"].append(f"incomplete_ranged_weapon:{model.profile.id}")
            elif any(w.id in ("WG_CROSSBOW", "WG_ELF_BOW", "WG_ORC_BOW")
                     for w in model.effective_wargear):
                result["ranged_wargear_without_profile"].append(model.profile.id)
        if result["ranged_wargear_without_profile"]:
            result["issues"].append("unresolved_ranged_weapon")
    except Exception as exc:
        result["issues"].append(f"runtime_audit_failed:{type(exc).__name__}:{exc}")
    result["status"] = "option_audit_passed" if not result["issues"] else "blocked"
    return result


def audit(root=FIXTURE_DIR, importer=load_reference_army_with_platforms):
    results = [evaluate_one(k, filename, root=root, importer=importer)
               for k, (filename, _alignment, _archetype) in FIXTURES.items()]
    return {
        "stage": "B8-B", "scope": "selected_options_and_ranged_profiles",
        "results": results,
        "option_audit_passed": sum(x["status"] == "option_audit_passed" for x in results),
        "candidates": len(results),
        "full_special_rules_approved": False,
        "archetype_review_approved": False,
        "calibration_anchors_approved": False,
        "production_scoring_modified": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2))
