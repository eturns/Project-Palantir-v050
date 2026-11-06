"""Project Palantír — DEV-082-A3-2H-1 support/aggregation audit.

Author: Edward Turns (Project Lead)
OpenAI ChatGPT (Technical Lead)

Read-only architectural inventory and explicit model-role conservation contract.
Potential spear-equipped supporters are NOT automatically active supporters.
No additional attacks, candidate offence density, or production modification.
"""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

SUPPORT_WARGEAR_IDS = frozenset({"WG_SPEAR", "WG_WAR_SPEAR"})
SOURCE_CONTRACT = {
    "combat_participant.py": {
        "class": "CombatParticipant",
        "attributes": ("duel_dice", "contributes_fight", "can_make_strikes"),
    },
    "combat_side.py": {
        "class": "CombatSide",
        "attributes": ("participants",),
        "properties": ("total_duel_dice", "highest_fight", "strike_participants"),
    },
    "duel_probability.py": {
        "functions": ("calculate_combat_side_duel_probability",),
    },
    "army_offence_capability.py": {
        "functions": ("calculate_army_offensive_output_density",),
    },
    "profile_offensive_combat_score.py": {
        "functions": ("calculate_profile_offensive_combat_score",),
    },
}


def _class_has_attributes(node: ast.ClassDef) -> set[str]:
    fields = set()
    for child in node.body:
        if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            fields.add(child.target.id)
    return fields


def inspect_source_contract(src_dir: str | Path) -> dict:
    """Inspect real repository source, report absent features rather than guess."""
    root = Path(src_dir)
    results = {}
    for filename, contract in SOURCE_CONTRACT.items():
        path = root / filename
        if not path.is_file():
            results[filename] = {"status": "missing_file", "missing": [filename]}
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (UnicodeError, SyntaxError, OSError) as exc:
            results[filename] = {"status": "unreadable", "reason": str(exc)}
            continue
        classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
        functions = {
            n.name for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        missing = []
        for name in contract.get("functions", ()):
            if name not in functions:
                missing.append(name)
        clsname = contract.get("class")
        if clsname:
            cls = classes.get(clsname)
            if cls is None:
                missing.append(clsname)
            else:
                attrs = _class_has_attributes(cls)
                missing.extend(name for name in contract.get("attributes", ())
                               if name not in attrs)
                methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}
                missing.extend(name for name in contract.get("properties", ())
                               if name not in methods)
        results[filename] = {
            "status": "present" if not missing else "missing_contract",
            "missing": missing,
        }
    return {
        "status": ("verified" if all(x["status"] == "present" for x in results.values())
                   else "incomplete"),
        "source_probes": results,
        "support_duel_dice_contract": "CombatParticipant.duel_dice -> CombatSide.total_duel_dice",
        "support_fight_contract": "CombatParticipant.contributes_fight -> CombatSide.highest_fight",
        "strike_exclusion_contract": "CombatParticipant.can_make_strikes -> CombatSide.strike_participants",
        "legacy_density_contract": "sum(per_model_offence_score * quantity) * 100 / army_points",
        "legacy_support_modelled": False,
        "configured_profile_support_aggregated": False,
        "notes": [
            "Source presence verifies interfaces, not rule completeness or live integration.",
            "CombatSide has role-capable components; legacy army density uses independent model scores.",
            "Supporter Fight/dice/strikes must be evaluated in one joint combat, not added to an independent fighter score.",
        ],
    }


def audit_army_support_inventory(army, *, key: str) -> dict:
    """Count potential support equipment, preserving imported configuration rows."""
    models, potential = 0, 0
    rows = []
    for index, entry in enumerate(army.entries, start=1):
        if not entry.counts_as_model:
            continue
        n = entry.quantity
        if type(n) is not int or n <= 0:
            raise ValueError("Invalid fielded quantity")
        configured = entry.configured_profile
        if configured is None:
            raise ValueError("Model entry lacks configured profile")
        ids = tuple(sorted({w.id for w in configured.effective_wargear}))
        support = tuple(sorted(set(ids) & SUPPORT_WARGEAR_IDS))
        models += n
        potential += n if support else 0
        rows.append({
            "entry_index": index, "profile_id": configured.profile.id,
            "quantity": n, "support_wargear_ids": list(support),
            "potential_support_model": bool(support),
            "actual_support_role": "unknown",
            "independent_combat_role": "not_assigned",
        })
    if models != army.model_count():
        raise ValueError("Army model count mismatch")
    return {
        "key": key,
        "status": "audited", "models": models,
        "potential_support_equipped_models": potential,
        "unverified_support_deployment_models": potential,
        "conditional_support_combats_calculated": 0,
        "allocation_status": "no_battlefield_roles_inferred",
        "entries": rows,
    }


def validate_combat_role_allocation(model_ids, combats) -> dict:
    """Validate explicit identity conservation; never calculate model probabilities.

    Each combat provides ``fighter_ids`` and ``supporter_ids``.
    One model may appear in *one* combat and *one* role only. A support-only
    combat is illegal. No weapons, proximity, or rules are assumed here.
    """
    ids = list(model_ids)
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate model identifiers in roster")
    if not all(isinstance(x, str) and x.strip() for x in ids):
        raise ValueError("Model identifiers must be nonblank strings")
    roster = set(ids)
    used = set()
    entries = []
    for i, combat in enumerate(combats):
        fighters = combat["fighter_ids"]
        supporters = combat["supporter_ids"]
        if not fighters:
            raise ValueError("A combat requires a fighting model")
        participants = list(fighters) + list(supporters)
        if len(participants) != len(set(participants)):
            raise ValueError("Model assigned more than one role in the same combat")
        if not set(participants) <= roster:
            raise ValueError("Combat includes non-roster model")
        if used.intersection(participants):
            raise ValueError("Model allocated to more than one combat")
        used.update(participants)
        entries.append({
            "combat_index": i,
            "fighter_count": len(fighters),
            "supporter_count": len(supporters),
            "conditional_combat_result": None,
            "support_rules_verified": False,
        })
    return {
        "status": "identity_conservation_only",
        "roster_models": len(roster),
        "allocated_models": len(used),
        "unallocated_models": len(roster - used),
        "fighters": sum(x["fighter_count"] for x in entries),
        "supporters": sum(x["supporter_count"] for x in entries),
        "combat_count": len(entries),
        "combats": entries,
        "score": None,
        "no_double_counting_verified": True,
        "support_legality_verified": False,
    }


def build_six_army_support_audit(*, fixtures, loader, src_dir) -> dict:
    """Fail visibly per army and preserve unverified architectural findings."""
    source = inspect_source_contract(src_dir)
    rows = []
    for key, path in fixtures:
        try:
            army = loader(path)
            result = audit_army_support_inventory(army, key=key)
        except Exception as exc:
            result = {"key": key, "status": "blocked", "reason": f"{type(exc).__name__}: {exc}"}
        rows.append(result)
    audited = [r for r in rows if r["status"] == "audited"]
    return {
        "stage": "DEV-082-A3-2H-1",
        "validation_status": ("six_armies_audited" if len(rows) == 6
                              and len(audited) == 6 and source["status"] == "verified"
                              else "incomplete"),
        "armies_audited": len(audited), "armies_expected": len(rows),
        "models_examined": sum(r["models"] for r in audited),
        "potential_support_equipped_models": sum(r["potential_support_equipped_models"]
                                                 for r in audited),
        "source_contract": source,
        "rows": rows,
        "aggregation_blockers": [
            "no_explicit_per-model_fighter_or_supporter_allocation",
            "support_eligibility_and_position_not_verified",
            "joint_combat_probability_not_integrated_into_army_density",
            "charge_trapping_and_weapon_frequencies_not_inferred",
            "legacy_independent_model_contributions_must_not_be_double_counted",
        ],
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
